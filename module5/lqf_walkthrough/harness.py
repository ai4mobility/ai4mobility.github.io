"""AI4Mobility: one dispatcher, with chat-driven, reference, and OpenAI API front ends.

stdio: actual requests supplied by a human or an assistant; no hidden model call.
reference: deterministic Python LQF controller; explicitly NOT a language model.
openai: a language model generates structured requests through the Responses API.
"""
import argparse
from contextlib import redirect_stdout
import json
from pathlib import Path
import sys

from jsonschema import validate

from sumo_tools import SimulationTools


def definition(name, description, properties):
    return {"type": "function", "name": name, "description": description, "strict": True,
            "parameters": {"type": "object", "properties": properties,
                           "required": list(properties), "additionalProperties": False}}


TOOLS = [
    definition("start_simulation", "Build and start the through-only intersection; advance 30 s with NS green. Returns scenario configuration. Call once, then read_state.",
               {"seed": {"type": "integer", "minimum": 0, "maximum": 2147483647}}),
    definition("read_state", "Read SUMO time in seconds, current green, and stopped-vehicle queues for NS and EW. Does not advance time.", {}),
    definition("serve_green", "Serve the requested group for 10 s. If switching, first execute 3 s yellow and 2 s all-red. Advances SUMO time and returns the next observed state. This tool does not select the group for you.",
               {"group": {"type": "string", "enum": ["NS", "EW"]},
                "observed_time_s": {"type": "number", "description": "time_s from the latest observed state"}}),
    definition("finish_simulation", "After exactly six decisions, close SUMO and return measured metrics and an independent LQF decision audit. Does not clear remaining traffic.", {}),
]
TASK = """Run this AI4Mobility longest-queue-first demonstration with seed 7.
Start the simulation and read its state. At each decision choose the group (NS or EW)
with the larger total stopped-vehicle count. On a tie retain the current group.
Call serve_green with that group and the time of the state used for the decision.
Use each returned state for the next decision. After exactly six decisions call
finish_simulation, then explain the measured outcome. Do not claim that LQF beats
another controller: this task contains no comparison run."""


class Harness:
    def __init__(self, output, source):
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.simulation = SimulationTools(self.output)
        self.handlers = {tool["name"]: getattr(self.simulation, tool["name"]) for tool in TOOLS}
        self.schemas = {tool["name"]: tool["parameters"] for tool in TOOLS}
        self.completed = False
        self.source = source
        self.results_by_id = {}
        self.log = open(self.output / "conversation.jsonl", "w")
        self.record({"type": "setup", "request_source": source, "task": TASK, "tools": TOOLS})

    def record(self, event):
        self.log.write(json.dumps(event) + "\n")
        self.log.flush()

    def execute(self, call):
        """The execution boundary: a named request becomes an actual Python call."""
        call_id = call["call_id"]
        if call_id in self.results_by_id:
            old_call, output = self.results_by_id[call_id]
            if old_call != call:
                raise ValueError("A call_id cannot be reused for a different request.")
            return output  # Avoid executing a repeated action twice.
        self.record({"type": "request", "request_source": self.source, "item": call})
        try:
            name = call["name"]
            if name not in self.handlers:
                raise ValueError(f"Unknown tool: {name}")
            arguments = json.loads(call["arguments"])
            validate(arguments, self.schemas[name])
            with redirect_stdout(sys.stderr):
                result = self.handlers[name](**arguments)
            if name == "finish_simulation":
                self.completed = True
        except Exception as error:
            result = {"error": type(error).__name__, "message": str(error)}
        output = {"type": "function_call_output", "call_id": call_id, "output": json.dumps(result)}
        self.record({"type": "result", "item": output})
        self.results_by_id[call_id] = (dict(call), output)
        return output

    def close(self):
        self.simulation.close()
        self.log.close()


def run_openai(harness, model):
    """The model produces requests; the same local harness executes them."""
    from openai import OpenAI
    client = OpenAI()
    history = [{"role": "user", "content": TASK}]
    for _ in range(24):
        response = client.responses.create(
            model=model, input=history, tools=TOOLS, parallel_tool_calls=False,
            instructions="Use tools for all simulation observations. Follow the requested LQF rule. Finish only after successful finish_simulation. Report errors accurately.",
        )
        if response.status != "completed":
            raise RuntimeError(f"API response status: {response.status}")
        harness.record({"type": "model_response", "item": response.model_dump(mode="json")})
        history.extend(response.output)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            if not harness.completed:
                raise RuntimeError("The model stopped before completing the simulation task.")
            return response.output_text
        for call in calls:
            output = harness.execute({"type": "function_call", "call_id": call.call_id,
                                      "name": call.name, "arguments": call.arguments})
            history.append(output)
    raise RuntimeError("Model turn limit reached.")


def run_reference(harness):
    """A reproducible Python policy, not a mock or a claim of AI inference."""
    count = 0
    def call(name, **arguments):
        nonlocal count
        count += 1
        output = harness.execute({"type": "function_call", "call_id": f"reference_{count:03}",
                                  "name": name, "arguments": json.dumps(arguments)})
        result = json.loads(output["output"])
        if "error" in result:
            raise RuntimeError(result)
        return result
    call("start_simulation", seed=7)
    state = call("read_state")
    for _ in range(6):
        q = state["queue_vehicles_by_group"]
        group = state["current_green"] if q["NS"] == q["EW"] else max(q, key=q.get)
        state = call("serve_green", group=group, observed_time_s=state["time_s"])["state"]
    return call("finish_simulation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["stdio", "reference", "openai"], default="reference")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "runs" / "reference")
    parser.add_argument("--model", help="A tool-capable Responses API model ID; required for openai mode")
    args = parser.parse_args()
    if args.mode == "openai" and not args.model:
        parser.error("--model is required for openai mode")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Choose an empty output directory to preserve existing run evidence.")
    harness = Harness(args.output, {"stdio": "assistant_or_human_via_stdio", "reference": "deterministic_python_reference", "openai": "openai_responses_api"}[args.mode])
    try:
        if args.mode == "stdio":
            print(json.dumps({"ready": True, "task": TASK, "tools": TOOLS}), flush=True)
            for line in sys.stdin:
                if line.strip():
                    print(json.dumps(harness.execute(json.loads(line))), flush=True)
                if harness.completed:
                    break
        elif args.mode == "reference":
            print(json.dumps(run_reference(harness), indent=2))
        else:
            print(run_openai(harness, args.model))
    finally:
        harness.close()


if __name__ == "__main__":
    main()
