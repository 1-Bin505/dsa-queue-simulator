import time
from collections import deque
import threading

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
    
    def size(self):
        return len(self.queue)
    
    def __iter__(self):
        return iter(self.queue)

lane = {
    "AL1": Queue(), "AL2": Queue(), "AL3": Queue(),
    "BL1": Queue(), "BL2": Queue(), "BL3": Queue(),
    "CL1": Queue(), "CL2": Queue(), "CL3": Queue(),
    "DL1": Queue(), "DL2": Queue(), "DL3": Queue(),
}

LaneA_light = LaneB_light = LaneC_light = LaneD_light = "RED"
TIME_PER_VEHICLE = 1  # seconds per vehicle
PRIORITY_THRESHOLD = 5  # AL2 priority threshold

def is_priority_active():
    """Check if AL2 has priority (≥5 vehicles)"""
    return lane["AL2"].size() >= PRIORITY_THRESHOLD

def calculate_vehicles_to_serve(lanes_to_check):
    """Calculate average vehicles to serve from normal lanes"""
    if not lanes_to_check:
        return 0
    
    total_vehicles = sum(lane[l].size() for l in lanes_to_check)
    n = len(lanes_to_check)
    
    # |V| = (1/n) * Σ|Li|
    vehicles_to_serve = max(1, int(total_vehicles / n))
    return vehicles_to_serve

def light_changer():
    global LaneA_light, LaneB_light, LaneC_light, LaneD_light
    
    while True:
        if paused:
            time.sleep(0.2)
            continue
        
        # Check if AL2 needs priority service
        al2_priority = is_priority_active()
        
        # Phase 1: Lane A & C (GREEN), Lane B & D (RED)
        LaneA_light = LaneC_light = "GREEN"
        LaneB_light = LaneD_light = "RED"
        
        # If AL2 has priority, serve it in this phase
        if al2_priority:
            # Calculate time based on AL2 queue only
            vehicles_to_serve = lane["AL2"].size()
            green_time = vehicles_to_serve * TIME_PER_VEHICLE
            print(f"[PRIORITY] AL2 has {vehicles_to_serve} vehicles - serving immediately")
        else:
            # Normal calculation for Lane A/C phase
            # Normal lanes: BL2, CL2, DL2 (AL2 is priority, so not counted)
            normal_lanes = ["BL2", "CL2", "DL2"]
            vehicles_to_serve = calculate_vehicles_to_serve(normal_lanes)
            green_time = max(8, vehicles_to_serve * TIME_PER_VEHICLE)
            print(f"[NORMAL] A/C Phase: Serving {vehicles_to_serve} vehicles, time={green_time}s")
        
        time.sleep(green_time)
        
        # Phase 2: Lane B & D (GREEN), Lane A & C (RED)
        LaneA_light = LaneC_light = "RED"
        LaneB_light = LaneD_light = "GREEN"
        
        # Calculate for Lane B/D phase
        # If AL2 was priority, it's served, so now count it as normal
        # Normal lanes: AL2 (if <5), BL3, CL3, DL3
        if is_priority_active():
            normal_lanes = ["BL3", "CL3", "DL3"]
        else:
            normal_lanes = ["AL2", "BL3", "CL3", "DL3"]
        
        vehicles_to_serve = calculate_vehicles_to_serve(normal_lanes)
        green_time = max(8, vehicles_to_serve * TIME_PER_VEHICLE)
        print(f"[NORMAL] B/D Phase: Serving {vehicles_to_serve} vehicles, time={green_time}s")
        
        time.sleep(green_time)

def generator():
    i = 0
    while True:
        if paused:
            time.sleep(0.2)
            continue
        
        # Add vehicles to left-turn lanes (L3)
        for l in ["AL3", "BL3", "CL3", "DL3"]:
            lane[l].enqueue(f"{l}_{i}")
        print(f"[GEN] Added vehicles to L3 lanes: {i}")
        time.sleep(5)
        
        # Add vehicles to main lanes (L2)
        for l in ["AL2", "BL2", "CL2", "DL2"]:
            lane[l].enqueue(f"{l}_{i}")
        print(f"[GEN] Added vehicles to L2 lanes: {i} | AL2 size: {lane['AL2'].size()}")
        i += 1
        time.sleep(5)

def traversal():
    while True:
        if paused:
            time.sleep(0.2)
            continue
        
        # Lane A & C serving (when GREEN)
        if LaneA_light == "GREEN":
            # Prioritize AL3 (left turn, free lane)
            if not lane["AL3"].is_empty():
                vehicle = lane["AL3"].dequeue()
                move_events.append(("AL3", "CL1"))
                print(f"[MOVE] {vehicle}: AL3 → CL1")
            # Then serve AL2 (priority/normal lane)
            elif not lane["AL2"].is_empty():
                vehicle = lane["AL2"].dequeue()
                move_events.append(("AL2", "BL1"))
                print(f"[MOVE] {vehicle}: AL2 → BL1")
        
        if LaneC_light == "GREEN":
            if not lane["CL3"].is_empty():
                vehicle = lane["CL3"].dequeue()
                move_events.append(("CL3", "BL1"))
                print(f"[MOVE] {vehicle}: CL3 → BL1")
            elif not lane["CL2"].is_empty():
                vehicle = lane["CL2"].dequeue()
                move_events.append(("CL2", "DL1"))
                print(f"[MOVE] {vehicle}: CL2 → DL1")
        
        # Lane B & D serving (when GREEN)
        if LaneB_light == "GREEN":
            if not lane["BL3"].is_empty():
                vehicle = lane["BL3"].dequeue()
                move_events.append(("BL3", "DL1"))
                print(f"[MOVE] {vehicle}: BL3 → DL1")
            elif not lane["BL2"].is_empty():
                vehicle = lane["BL2"].dequeue()
                move_events.append(("BL2", "AL1"))
                print(f"[MOVE] {vehicle}: BL2 → AL1")
        
        if LaneD_light == "GREEN":
            if not lane["DL3"].is_empty():
                vehicle = lane["DL3"].dequeue()
                move_events.append(("DL3", "AL1"))
                print(f"[MOVE] {vehicle}: DL3 → AL1")
            elif not lane["DL2"].is_empty():
                vehicle = lane["DL2"].dequeue()
                move_events.append(("DL2", "CL1"))
                print(f"[MOVE] {vehicle}: DL2 → CL1")
        
        time.sleep(TIME_PER_VEHICLE)

# Start threads
if __name__ == "__main__":
    threading.Thread(target=light_changer, daemon=True).start()
    threading.Thread(target=generator, daemon=True).start()
    threading.Thread(target=traversal, daemon=True).start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulation stopped")