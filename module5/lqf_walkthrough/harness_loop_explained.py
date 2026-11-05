"""AI4Mobility: the complete harness loop, annotated to match the loop diagram.

This teaching version reuses TASK and TOOLS from harness.py and the real SUMO
helper implementations from sumo_tools.py. It does not replace harness.py,
which additionally records a transcript and caches repeated call IDs.

Requires the walkthrough's requirements.txt, working SUMO binaries, and the
OPENAI_API_KEY and OPENAI_MODEL environment variables. Running this script
makes real model API requests and starts SUMO through the registered helpers.

Diagram: Shared/Figures/harness_loop/AI4Mobility_Harness_Loop.drawio
Official protocol: https://developers.openai.com/api/docs/guides/function-calling
"""
import json
import os
from pathlib import Path
from tempfile import mkdtemp

from jsonschema import validate
from openai import OpenAI

from harness import TASK, TOOLS
from sumo_tools import SimulationTools


def run_harness(client, model, simulation):
    # SETUP: store callable functions; these lines do not run them.
    handlers = {
        "start_simulation": simulation.start_simulation,
        "read_state": simulation.read_state,
        "serve_green": simulation.serve_green,
        "finish_simulation": simulation.finish_simulation,
    }
    schemas = {tool["name"]: tool["parameters"] for tool in TOOLS}
    history = [{"role": "user", "content": TASK}]

    for turn in range(24):
        # A. AI MODEL / NEXT MODEL REQUEST
        # First turn: send the task. Later turns: also send prior results.
        response = client.responses.create(
            model=model,
            input=history,
            tools=TOOLS,
            parallel_tool_calls=False,
            instructions=(
                "Use tools for simulation observations and follow the LQF rule. "
                "Finish only after successful finish_simulation. "
                "Report errors accurately."
            ),
        )
        if response.status != "completed":
            raise RuntimeError(f"API response status: {response.status}")

        # B. TOOL REQUEST: retain all response items, including reasoning items.
        history.extend(response.output)
        calls = [item for item in response.output if item.type == "function_call"]

        # EXIT: a final answer ends the loop after the simulation is finished.
        if not calls:
            if not simulation.finished:
                raise RuntimeError("The model stopped before finishing the task.")
            return response.output_text

        for call in calls:
            try:
                # C. HARNESS ROLE 1: decode and validate the requested call.
                name = call.name
                if name not in handlers:
                    raise ValueError(f"Unknown tool: {name}")
                arguments = json.loads(call.arguments)
                validate(arguments, schemas[name])

                # D. FUNCTION CALL -> TOOL FUNCTION -> RETURN VALUE
                handler = handlers[name]       # Retrieve the callable.
                result = handler(**arguments)  # Execute it; capture its return.

            except Exception as error:
                # A failed call supplies error feedback for the next model turn.
                result = {"error": type(error).__name__, "message": str(error)}

            # E. HARNESS ROLE 2: serialize and identify the tool result.
            tool_result = {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),  # Python object -> JSON string.
            }

            # F. HARNESS ROLE 2: update local history. No API request here.
            history.append(tool_result)

        # G. LOOP BACK TO A: the next responses.create sends updated history.

    raise RuntimeError("Model turn limit reached.")


if __name__ == "__main__":
    model = os.environ["OPENAI_MODEL"]
    client = OpenAI()  # Reads OPENAI_API_KEY from the environment.
    runs = Path(__file__).parent / "runs"
    runs.mkdir(exist_ok=True)
    output = Path(mkdtemp(prefix="explained_", dir=runs))
    simulation = SimulationTools(output)
    try:
        print(run_harness(client, model, simulation))
    finally:
        simulation.close()
