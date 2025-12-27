import time
from collections import deque
import threading
import random

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
TIME_PER_VEHICLE = 1  
PRIORITY_TRIGGER_THRESHOLD = 10
PRIORITY_DEACTIVATE_THRESHOLD = 5


is_priority_on = False 

def is_priority_active():
   
    global is_priority_on
    al2_size = lane["AL2"].size()
    
    if al2_size > PRIORITY_TRIGGER_THRESHOLD:
        is_priority_on = True
    elif al2_size <= PRIORITY_DEACTIVATE_THRESHOLD:
        is_priority_on = False
        
    return is_priority_on

def calculate_vehicles_to_serve(lanes_to_check):
   
    if not lanes_to_check:
        return 0
    
    total_vehicles = sum(lane[l].size() for l in lanes_to_check)
    n = len(lanes_to_check)
    
    vehicles_to_serve = max(1, int(total_vehicles / n))
    return vehicles_to_serve

def light_changer():
    global LaneA_light, LaneB_light, LaneC_light, LaneD_light
    
    while True:
        if paused:
            time.sleep(0.2)
            continue

        al2_priority_active = is_priority_active()
        
        
        LaneA_light = LaneC_light = "GREEN"
        LaneB_light = LaneD_light = "RED"
        
        if al2_priority_active:
            
            vehicles_to_serve = lane["AL2"].size()
            green_time = vehicles_to_serve * TIME_PER_VEHICLE
            print(f"[PRIORITY] AL2 is active ({lane['AL2'].size()} vehicles). Serving for {green_time}s.")
        else:
            
            normal_lanes = ["AL3", "CL3", "AL2", "CL2"]
            vehicles_to_serve = calculate_vehicles_to_serve(normal_lanes)
            green_time = max(8, vehicles_to_serve * TIME_PER_VEHICLE)
            print(f"[NORMAL] A/C Phase. Time={green_time}s")
        
        time.sleep(green_time)
        
       
        LaneA_light = LaneC_light = "RED"
        LaneB_light = LaneD_light = "GREEN"
        
       
        normal_lanes = ["BL3", "DL3", "BL2", "DL2"]
        vehicles_to_serve = calculate_vehicles_to_serve(normal_lanes)
        green_time = max(8, vehicles_to_serve * TIME_PER_VEHICLE)
        print(f"[NORMAL] B/D Phase. Time={green_time}s")
        
        time.sleep(green_time)

def generator():
    i = 0
    while True:
        if paused:
            time.sleep(0.2)
            continue
        
      
        for l in ["AL3", "BL3", "CL3", "DL3"]:
            lane[l].enqueue(f"{l}_{i}")
        print(f"[GEN] Added vehicles to L3 lanes: {i}")
        time.sleep(5)
        
        
        for l in ["AL2", "BL2", "CL2", "DL2"]:
            lane[l].enqueue(f"{l}_{i}")
        print(f"[GEN] Added vehicles to L2 lanes: {i} | AL2 size: {lane['AL2'].size()}")
        i += 1
        time.sleep(5)

def traversal():
   
    L3_FLOW = {
        "DL3": "AL1",
        "AL3": "CL1",
        "CL3": "BL1",
        "BL3": "DL1",
    }
    
   
    L2_FLOW = {
        "AL2": ["BL2", "DL2"], 
        "BL2": ["AL2", "CL2"], 
        "CL2": ["DL2", "AL2"], 
        "DL2": ["CL2", "BL2"], 
    }

    while True:
        if paused:
            time.sleep(0.2)
            continue
        
       
        if LaneA_light == "GREEN":
           
            if not lane["AL3"].is_empty():
                vehicle = lane["AL3"].dequeue()
                move_events.append(("AL3", L3_FLOW["AL3"]))
                print(f"[MOVE] {vehicle}: AL3 → {L3_FLOW['AL3']} (L3 Turn)")
            
            
            elif not lane["AL2"].is_empty():
                vehicle = lane["AL2"].dequeue()
                destination = random.choice(L2_FLOW["AL2"])
                move_events.append(("AL2", destination))
                print(f"[MOVE] {vehicle}: AL2 → {destination} (L2 S/R)")

        if LaneC_light == "GREEN":
           
            if not lane["CL3"].is_empty():
                vehicle = lane["CL3"].dequeue()
                move_events.append(("CL3", L3_FLOW["CL3"]))
                print(f"[MOVE] {vehicle}: CL3 → {L3_FLOW['CL3']} (L3 Turn)")

           
            elif not lane["CL2"].is_empty():
                vehicle = lane["CL2"].dequeue()
                destination = random.choice(L2_FLOW["CL2"])
                move_events.append(("CL2", destination))
                print(f"[MOVE] {vehicle}: CL2 → {destination} (L2 S/R)")
        
       
        if LaneB_light == "GREEN":
           
            if not lane["BL3"].is_empty():
                vehicle = lane["BL3"].dequeue()
                move_events.append(("BL3", L3_FLOW["BL3"]))
                print(f"[MOVE] {vehicle}: BL3 → {L3_FLOW['BL3']} (L3 Turn)")

            
            elif not lane["BL2"].is_empty():
                vehicle = lane["BL2"].dequeue()
                destination = random.choice(L2_FLOW["BL2"])
                move_events.append(("BL2", destination))
                print(f"[MOVE] {vehicle}: BL2 → {destination} (L2 S/R)")
        
        if LaneD_light == "GREEN":
           
            if not lane["DL3"].is_empty():
                vehicle = lane["DL3"].dequeue()
                move_events.append(("DL3", L3_FLOW["DL3"]))
                print(f"[MOVE] {vehicle}: DL3 → {L3_FLOW['DL3']} (L3 Turn)")

           
            elif not lane["DL2"].is_empty():
                vehicle = lane["DL2"].dequeue()
                destination = random.choice(L2_FLOW["DL2"])
                move_events.append(("DL2", destination))
                print(f"[MOVE] {vehicle}: DL2 → {destination} (L2 S/R)")
        
        time.sleep(TIME_PER_VEHICLE)


if __name__ == "__main__":
    
    def user_input_handler():
        global paused
        while True:
            cmd = input("Enter 'p' to pause/unpause: ").strip().lower()
            if cmd == 'p':
                paused = not paused
                print(f"Simulation {'PAUSED' if paused else 'RUNNING'}")
            elif cmd == 'q':
                print("Exiting...")
                exit(0)
    
  
    threading.Thread(target=light_changer, daemon=True).start()
    threading.Thread(target=generator, daemon=True).start()
    threading.Thread(target=traversal, daemon=True).start()
    

    user_input_handler()