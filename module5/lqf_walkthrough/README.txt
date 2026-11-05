AI4Mobility: longest-queue-first SUMO walkthrough

This example contains actual SUMO 1.28.0 measurements. The requests in
runs/assistant_walkthrough/conversation.jsonl were written by the assistant
in the Codex chat, sent through the stdio harness, and chosen after observing
each returned state. This was not a separate call to the OpenAI API.
The reference_verified run uses an explicitly deterministic Python policy.
The two modes produced identical simulation summaries.

Scenario and task
One synthetic four-arm intersection, one lane per approach, through traffic
only, no pedestrians or turns. Demand is a seeded, explicit list of 59 vehicles
departing during seconds 0-59. Vehicle-driving randomness is disabled (sigma=0).
First hold NS green for a 30 s startup period. Then make exactly six decisions.
At each decision sum stopped vehicles over the lanes in each group (NS or EW),
choose the larger sum, and retain the current group on ties. A stopped vehicle
has speed below 0.1 m/s. This is a queue proxy, not a physical queue length.
Each action gives 10 s green. Switching adds 3 s yellow and 2 s all-red first.
These intervals are teaching assumptions, not a timing recommendation.
The task finishes after six decisions even if vehicles remain in the network.
The initial 30 s period is a demonstration setup, not a claim of steady state.

Responsibilities
scenario.py builds all network, signal, and demand XML files locally.
sumo_tools.py provides start_simulation, read_state, serve_green, and
finish_simulation. These helpers call TraCI and own the running connection.
harness.py sends descriptions to a model, validates requests, dispatches
ordinary Python functions, and returns their results with matching call_id.
The serve_green helper never selects the winning group. The caller does.
finish_simulation audits the choices independently after execution.
Calls use a unique ID. Exact repeated IDs return their cached result so the
same action is not accidentally executed twice during the same process.
Observed simulation times reject stale actions. Errors return structured
messages. This is a small teaching harness, not a production controller.

How to run
From this folder, create a Python environment and install requirements.txt:
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
Run the reproducible Python reference (no API credential required):
  .venv/bin/python harness.py --mode reference --output runs/my_reference
Run a language model through the Responses API (uses API credits):
  .venv/bin/python harness.py --mode openai --model YOUR_MODEL_ID --output runs/my_model
The API mode requires OPENAI_API_KEY already configured in your environment.
Choose a tool-capable model available to your account. This API path was
checked against documentation but was not called or integration-tested here.
To send requests manually, use --mode stdio and send one JSON object per line:
  {"type":"function_call","call_id":"call_001","name":"start_simulation","arguments":"{\"seed\":7}"}
Choose a new, empty output folder for every run; old evidence is not overwritten.
The bundled eclipse-sumo package supplies the executable, so the example does
not depend on the user's pre-existing system SUMO installation.
TraCI requires the Python process and SUMO to communicate over localhost.

Verified run
Decision time   NS stopped   EW stopped   Requested green   Time after action
30 s             0            4          EW                45 s
45 s             8            2          NS                60 s
60 s             1           13          EW                75 s
75 s            12            2          NS                90 s
90 s             0            8          EW               105 s
105 s            2            0          NS               120 s
These choices alternate because the measured queues change. Alternation is
not part of the policy; retaining the current group is permitted.
At 120 s, 50 vehicles have arrived and 9 remain; 1 of those 9 is stopped.
The mean total stopped-vehicle count is 9.6 over the 90 control samples,
including yellow and all-red intervals, excluding the 30 startup samples.
All 6 decisions follow LQF. There are no recorded collisions or teleports.
There is no baseline comparison and no claim that LQF improves performance.
Frequent switching has lost-time costs; simple LQF can also neglect a smaller
queue. A broader experiment should compare fixed-time control under matched
demand, time horizons, and seeds, and measure delay and maximum waiting time.

Saved evidence
conversation.jsonl: task and tool schemas, every request, every returned output.
decisions.json: state before and after each action, with executed stages.
steps.json: every 1 s simulation interval and the observed phase and queue.
summary.json: measured totals and the independent policy audit.
tripinfo.xml: SUMO output, including unfinished vehicles.
scenario/: editable SUMO input files.
Check the saved evidence without running a model or SUMO:
  .venv/bin/python verify_run.py

Sources checked November 4, 2026
https://developers.openai.com/api/docs/guides/function-calling
https://sumo.dlr.de/docs/TraCI/Lane_Value_Retrieval.html
https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html

The SUMO helper deliberately manages all phase transitions itself: setPhase
selects a known phase, setPhaseDuration(10000) prevents an automatic change,
then simulationStep advances the requested number of 1 s steps. It replaces
that phase explicitly at the next stage. The 10000 s hold is not a delivered
green duration; the helper actually advances only 3, 2, or 10 s as appropriate.
