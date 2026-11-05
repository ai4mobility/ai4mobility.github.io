"""AI4Mobility: build a synthetic, through-only, four-arm SUMO intersection."""
from pathlib import Path
import random
import subprocess
import xml.etree.ElementTree as ET

import sumo

SUMO_BIN = Path(sumo.SUMO_HOME) / "bin"
LANES = {"NS": ["N_in_0", "S_in_0"], "EW": ["E_in_0", "W_in_0"]}
PHASE = {"NS": 0, "EW": 3}
YELLOW = {"NS": 1, "EW": 4}
ALL_RED = {"NS": 2, "EW": 5}
GREEN_SECONDS, YELLOW_SECONDS, ALL_RED_SECONDS = 10, 3, 2
WARMUP_SECONDS, DECISION_LIMIT = 30, 6


def build_scenario(folder, seed=7):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    nodes = ET.Element("nodes")
    ET.SubElement(nodes, "node", id="J", x="0", y="0", type="traffic_light")
    for name, (x, y) in {"N": (0, 300), "S": (0, -300), "E": (300, 0), "W": (-300, 0)}.items():
        ET.SubElement(nodes, "node", id=name, x=str(x), y=str(y))
    edges, connections = ET.Element("edges"), ET.Element("connections")
    for origin, destination in [("N", "S"), ("S", "N"), ("E", "W"), ("W", "E")]:
        ET.SubElement(edges, "edge", {"id": origin + "_in", "from": origin, "to": "J", "numLanes": "1", "speed": "13.89"})
        ET.SubElement(edges, "edge", {"id": origin + "_out", "from": "J", "to": origin, "numLanes": "1", "speed": "13.89"})
        ET.SubElement(connections, "connection", {"from": origin + "_in", "to": destination + "_out", "fromLane": "0", "toLane": "0"})
    for name, root in [("nodes.nod.xml", nodes), ("edges.edg.xml", edges), ("connections.con.xml", connections)]:
        ET.ElementTree(root).write(folder / name, encoding="utf-8", xml_declaration=True)
    subprocess.run([
        str(SUMO_BIN / "netconvert"), "--node-files", str(folder / "nodes.nod.xml"),
        "--edge-files", str(folder / "edges.edg.xml"), "--connection-files", str(folder / "connections.con.xml"),
        "--output-file", str(folder / "intersection.net.xml"), "--no-turnarounds", "true",
    ], check=True, capture_output=True, text=True)
    net = ET.parse(folder / "intersection.net.xml")
    groups = {int(c.get("linkIndex")): ("NS" if c.get("from")[0] in "NS" else "EW")
              for c in net.iter("connection") if c.get("tl") == "J"}
    extra = ET.Element("additional")
    logic = ET.SubElement(extra, "tlLogic", id="J", type="static", programID="lqf", offset="0")
    for group in ["NS", "EW"]:
        for color, seconds in [("G", 10000), ("y", YELLOW_SECONDS), ("r", ALL_RED_SECONDS)]:
            state = "".join(color if groups[i] == group else "r" for i in range(len(groups)))
            ET.SubElement(logic, "phase", duration=str(seconds), state=state)
    ET.ElementTree(extra).write(folder / "signals.add.xml", encoding="utf-8", xml_declaration=True)
    routes = ET.Element("routes")
    ET.SubElement(routes, "vType", id="car", accel="2.6", decel="4.5", sigma="0", length="5", minGap="2.5")
    rng, departures = random.Random(seed), []
    for origin, destination in [("N", "S"), ("S", "N"), ("E", "W"), ("W", "E")]:
        ET.SubElement(routes, "route", id=origin, edges=f"{origin}_in {destination}_out")
        # A reproducible finite demand pulse; vehicles are explicit, not resampled by SUMO.
        for second in range(60):
            if rng.random() < (0.24 if origin in "NS" else 0.18):
                departures.append((second, origin))
    for index, (second, origin) in enumerate(sorted(departures)):
        ET.SubElement(routes, "vehicle", id=f"{origin}_{index}", type="car", route=origin,
                      depart=str(second), departLane="0", departSpeed="max")
    ET.ElementTree(routes).write(folder / "demand.rou.xml", encoding="utf-8", xml_declaration=True)
    return len(departures)
