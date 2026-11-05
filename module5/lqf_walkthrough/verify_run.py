"""Check measured execution evidence without rerunning SUMO or calling a model."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
run = ROOT / "runs" / "assistant_walkthrough"
summary = json.loads((run / "summary.json").read_text())
reference = json.loads((ROOT / "runs" / "reference_verified" / "summary.json").read_text())
decisions = json.loads((run / "decisions.json").read_text())
steps = json.loads((run / "steps.json").read_text())
events = [json.loads(line) for line in (run / "conversation.jsonl").read_text().splitlines()]
requests = [event["item"] for event in events if event["type"] == "request"]
results = [event["item"] for event in events if event["type"] == "result"]
assert summary == reference, "Chat-driven and deterministic reference runs differ."
assert len(requests) == len(results) == 9
assert [item["call_id"] for item in requests] == [item["call_id"] for item in results]
assert all("error" not in json.loads(item["output"]) for item in results)
assert len(decisions) == 6
assert steps[0]["from_s"] == 0 and steps[-1]["to_s"] == summary["end_time_s"]
assert all(b["from_s"] == a["to_s"] for a, b in zip(steps, steps[1:]))
assert all(step["to_s"] - step["from_s"] == 1 for step in steps)
for decision in decisions:
    before, after = decision["before"], decision["after"]
    q = before["queue_vehicles_by_group"]
    group = before["current_green"] if q["NS"] == q["EW"] else max(q, key=q.get)
    assert group == decision["requested_group"]
    window = [step for step in steps if before["time_s"] <= step["from_s"] < after["time_s"]]
    target_phase = 0 if group == "NS" else 3
    expected_phases = [target_phase] * 10
    if group != before["current_green"]:
        yellow = 1 if before["current_green"] == "NS" else 4
        expected_phases = [yellow] * 3 + [yellow + 1] * 2 + expected_phases
    assert [step["phase"] for step in window] == expected_phases
    assert after["current_green"] == group
assert summary["scheduled_vehicles"] == summary["departed_vehicles"]
assert summary["departed_vehicles"] == summary["arrived_vehicles"] + summary["final_state"]["vehicles_in_network"]
assert summary["collision_vehicle_events"] == summary["teleport_events"] == 0
print("PASS: 9 matched requests/results; 6 LQF choices; exact phase durations; vehicle accounting; identical reference results.")
print("OpenAI API mode is included but was not called or integration-tested.")
