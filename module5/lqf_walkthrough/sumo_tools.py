"""AI4Mobility tools: Python helpers call TraCI; the model never calls TraCI directly."""
import json
from pathlib import Path

import traci

from scenario import (SUMO_BIN, LANES, PHASE, YELLOW, ALL_RED, GREEN_SECONDS,
                      YELLOW_SECONDS, ALL_RED_SECONDS, WARMUP_SECONDS, DECISION_LIMIT, build_scenario)


class SimulationTools:
    def __init__(self, output):
        self.output = Path(output)
        self.connection = None
        self.started = False
        self.finished = False
        self.decisions = []
        self.steps = []
        self.arrived = 0
        self.departed = 0
        self.collisions = 0
        self.teleports = 0
        self.current_group = "NS"
        self.observed_time = None

    def start_simulation(self, seed):
        if self.started:
            raise ValueError("This harness allows one simulation per run.")
        self.total_demand = build_scenario(self.output / "scenario", seed)
        folder = self.output / "scenario"
        label = "ai4mobility_lqf"
        traci.start([
            str(SUMO_BIN / "sumo"), "-n", str(folder / "intersection.net.xml"),
            "-r", str(folder / "demand.rou.xml"), "-a", str(folder / "signals.add.xml"),
            "--step-length", "1", "--seed", str(seed), "--time-to-teleport", "-1",
            "--no-step-log", "true", "--duration-log.disable", "true",
            "--tripinfo-output", str(self.output / "tripinfo.xml"),
            "--tripinfo-output.write-unfinished", "true",
        ], label=label, stdout=open(self.output / "sumo.stdout.log", "w"))
        self.connection = traci.getConnection(label)
        self.started = True
        self.seed = seed
        self.version = self.connection.getVersion()[1]
        self._hold_phase(PHASE["NS"], WARMUP_SECONDS, "warmup")
        return {"status": "started", "time_s": self.connection.simulation.getTime(),
                "current_green": "NS", "decision_limit": DECISION_LIMIT,
                "green_seconds_per_decision": GREEN_SECONDS,
                "yellow_seconds": YELLOW_SECONDS, "all_red_seconds": ALL_RED_SECONDS,
                "queue_definition": "vehicles with speed below 0.1 m/s on incoming lanes",
                "lanes_by_group": LANES, "scheduled_vehicles": self.total_demand,
                "sumo_version": self.version, "next_action": "Call read_state."}

    def _require_running(self):
        if self.connection is None or self.finished:
            raise ValueError("Start a simulation before calling this tool; finished runs cannot resume.")

    def _snapshot(self):
        c = self.connection
        by_lane = {lane: c.lane.getLastStepHaltingNumber(lane) for lanes in LANES.values() for lane in lanes}
        return {"time_s": c.simulation.getTime(), "current_green": self.current_group,
                "halting_vehicles_by_lane": by_lane,
                "queue_vehicles_by_group": {group: sum(by_lane[lane] for lane in lanes) for group, lanes in LANES.items()},
                "decisions_completed": len(self.decisions),
                "vehicles_in_network": c.vehicle.getIDCount(),
                "vehicles_remaining_or_pending": c.simulation.getMinExpectedNumber()}

    def read_state(self):
        self._require_running()
        state = self._snapshot()
        self.observed_time = state["time_s"]
        return state

    def _hold_phase(self, phase, seconds, stage):
        c = self.connection
        if c.trafficlight.getPhase("J") != phase:
            c.trafficlight.setPhase("J", phase)
        # The helper owns all transitions. Prevent SUMO auto-switching during this interval.
        c.trafficlight.setPhaseDuration("J", 10000)
        for _ in range(seconds):
            start = c.simulation.getTime()
            c.simulationStep()
            self.arrived += c.simulation.getArrivedNumber()
            self.departed += c.simulation.getDepartedNumber()
            self.collisions += c.simulation.getCollidingVehiclesNumber()
            self.teleports += c.simulation.getStartingTeleportNumber()
            actual_phase = c.trafficlight.getPhase("J")
            if actual_phase != phase:
                raise RuntimeError("Signal unexpectedly changed during a controlled interval.")
            q = sum(c.lane.getLastStepHaltingNumber(lane) for lanes in LANES.values() for lane in lanes)
            self.steps.append({"from_s": start, "to_s": c.simulation.getTime(),
                               "stage": stage, "phase": actual_phase, "total_halting_vehicles": q})

    def serve_green(self, group, observed_time_s):
        self._require_running()
        if len(self.decisions) >= DECISION_LIMIT:
            raise ValueError("All six decisions are complete. Call finish_simulation.")
        if group not in PHASE:
            raise ValueError("group must be NS or EW.")
        now = self.connection.simulation.getTime()
        if self.observed_time is None or observed_time_s != self.observed_time or observed_time_s != now:
            raise ValueError("Read the current state before acting; observed_time_s must match it.")
        before = self._snapshot()
        stages = []
        if group != self.current_group:
            old_group = self.current_group
            self._hold_phase(YELLOW[old_group], YELLOW_SECONDS, "yellow")
            stages.append({"stage": old_group + "_yellow", "seconds": YELLOW_SECONDS})
            self._hold_phase(ALL_RED[old_group], ALL_RED_SECONDS, "all_red")
            stages.append({"stage": "all_red", "seconds": ALL_RED_SECONDS})
        self._hold_phase(PHASE[group], GREEN_SECONDS, "green")
        self.current_group = group
        stages.append({"stage": group + "_green", "seconds": GREEN_SECONDS})
        decision = {"decision": len(self.decisions) + 1, "before": before,
                    "requested_group": group, "executed_stages": stages}
        self.decisions.append(decision)
        after = self.read_state()
        decision["after"] = after
        return {"decision": len(self.decisions), "executed_stages": stages, "state": after}

    def finish_simulation(self):
        self._require_running()
        if len(self.decisions) != DECISION_LIMIT:
            raise ValueError("Complete exactly six decisions before finishing.")
        state = self._snapshot()
        control_steps = [step for step in self.steps if step["stage"] != "warmup"]
        checks = []
        for decision in self.decisions:
            before = decision["before"]
            q = before["queue_vehicles_by_group"]
            expected = before["current_green"] if q["NS"] == q["EW"] else max(q, key=q.get)
            checks.append(decision["requested_group"] == expected)
        result = {"status": "finished", "sumo_version": self.version, "seed": self.seed,
                  "warmup_s": WARMUP_SECONDS, "end_time_s": state["time_s"],
                  "control_duration_s": len(control_steps), "decisions_completed": len(self.decisions),
                  "lqf_decisions_verified": sum(checks), "all_decisions_followed_lqf": all(checks),
                  "mean_total_stopped_vehicles_during_control": round(sum(s["total_halting_vehicles"] for s in control_steps) / len(control_steps), 3),
                  "scheduled_vehicles": self.total_demand, "departed_vehicles": self.departed,
                  "arrived_vehicles": self.arrived, "vehicles_remaining_or_pending": state["vehicles_remaining_or_pending"],
                  "collision_vehicle_events": self.collisions, "teleport_events": self.teleports,
                  "final_state": state,
                  "scope": "Six decisions after a 30 s warmup; vehicles may remain. No performance comparison is claimed."}
        self.close()
        self.finished = True
        self.output.mkdir(parents=True, exist_ok=True)
        for name, data in [("summary.json", result), ("decisions.json", self.decisions), ("steps.json", self.steps)]:
            (self.output / name).write_text(json.dumps(data, indent=2) + "\n")
        return result

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
