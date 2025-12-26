import time
from collections import deque
paused = False
move_events = deque()
class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, element):
        self.queue.append(element)

    def dequeue(self):
        return self.queue.pop(0) if self.queue else None

    def is_empty(self):
        return len(self.queue) == 0

    def __iter__(self):
        return iter(self.queue)
lane = {
    "AL1": Queue(), "AL2": Queue(), "AL3": Queue(),
    "BL1": Queue(), "BL2": Queue(), "BL3": Queue(),
    "CL1": Queue(), "CL2": Queue(), "CL3": Queue(),
    "DL1": Queue(), "DL2": Queue(), "DL3": Queue(),
}

LaneA_light = LaneB_light = LaneC_light = LaneD_light = "RED"


def light_changer():
    global LaneA_light, LaneB_light, LaneC_light, LaneD_light
    while True:
        LaneA_light = LaneC_light = "GREEN"
        LaneB_light = LaneD_light = "RED"
        time.sleep(8)

        LaneA_light = LaneC_light = "RED"
        LaneB_light = LaneD_light = "GREEN"
        time.sleep(8)


def generator():
    i = 0
    while True:
        if paused:
            time.sleep(0.2)
            continue

        for l in ["AL3", "BL3", "CL3", "DL3"]:
            lane[l].enqueue(f"{l}_{i}")

        time.sleep(5)

        for l in ["AL2", "BL2", "CL2", "DL2"]:
            lane[l].enqueue(f"{l}_{i}")

        i += 1
        time.sleep(5)

def traversal():
    global paused
    while True:
        if paused:
            time.sleep(0.2)
            continue

        if LaneA_light == "GREEN":
            if not lane["AL3"].is_empty():
                lane["AL3"].dequeue()
                move_events.append(("AL3", "CL1"))
            elif not lane["AL2"].is_empty():
                lane["AL2"].dequeue()
                move_events.append(("AL2", "BL1"))

        if LaneB_light == "GREEN":
            if not lane["BL3"].is_empty():
                lane["BL3"].dequeue()
                move_events.append(("BL3", "DL1"))
            elif not lane["BL2"].is_empty():
                lane["BL2"].dequeue()
                move_events.append(("BL2", "AL1"))

        if LaneC_light == "GREEN":
            if not lane["CL3"].is_empty():
                lane["CL3"].dequeue()
                move_events.append(("CL3", "BL1"))
            elif not lane["CL2"].is_empty():
                lane["CL2"].dequeue()
                move_events.append(("CL2", "DL1"))

        if LaneD_light == "GREEN":
            if not lane["DL3"].is_empty():
                lane["DL3"].dequeue()
                move_events.append(("DL3", "AL1"))
            elif not lane["DL2"].is_empty():
                lane["DL2"].dequeue()
                move_events.append(("DL2", "CL1"))

        time.sleep(1)
