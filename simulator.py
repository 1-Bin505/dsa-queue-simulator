import time
from collections import deque


lanes = {
    "AL1": deque(), "AL2": deque(), "AL3": deque(),  
    "BL1": deque(), "BL2": deque(), "BL3": deque(),
    "CL1": deque(), "CL2": deque(), "CL3": deque(),
    "DL1": deque(), "DL2": deque(), "DL3": deque(),
}


lights = {
    "A": "RED",
    "B": "RED",
    "C": "RED",
    "D": "RED"
}


def traffic_lights():
    while True:
        lights["A"] = lights["C"] = "GREEN"
        lights["B"] = lights["D"] = "RED"
        print("\nLights: A & C GREEN")
        time.sleep(8)

        lights["A"] = lights["C"] = "RED"
        lights["B"] = lights["D"] = "GREEN"
        print("\nLights: B & D GREEN")
        time.sleep(8)


def generate_cars():
    i = 1
    while True:
        lanes["AL3"].append(f"A3_{i}")
        lanes["BL3"].append(f"B3_{i}")
        lanes["CL3"].append(f"C3_{i}")
        lanes["DL3"].append(f"D3_{i}")
        print(f"Generated priority cars {i}")
        time.sleep(5)

        lanes["AL2"].append(f"A2_{i}")
        lanes["BL2"].append(f"B2_{i}")
        lanes["CL2"].append(f"C2_{i}")
        lanes["DL2"].append(f"D2_{i}")
        print(f"Generated normal cars {i}")
        i += 1
        time.sleep(5)

MOVEMENTS = {
    "A": [("AL3", "CL1"), ("AL2", "BL1")],
    "B": [("BL3", "DL1"), ("BL2", "AL1")],
    "C": [("CL3", "BL1"), ("CL2", "DL1")],
    "D": [("DL3", "AL1"), ("DL2", "CL1")]
}


def move_cars():
    while True:
        for road in ["A", "B", "C", "D"]:
            if lights[road] == "GREEN":
                for src, dst in MOVEMENTS[road]:
                    if lanes[src]:
                        car = lanes[src].popleft()
                        lanes[dst].append(car)
                        print(f"{car} moved {src} -> {dst}")
                        break
        time.sleep(1)


def print_status():
    while True:
        print("\nLane Status:")
        for k, v in lanes.items():
            print(f"{k}: {list(v)}")
        time.sleep(10)


if __name__ == "__main__":
    import threading

    threading.Thread(target=traffic_lights, daemon=True).start()
    threading.Thread(target=generate_cars, daemon=True).start()
    threading.Thread(target=move_cars, daemon=True).start()
    threading.Thread(target=print_status, daemon=True).start()

    while True:
        time.sleep(1)
