import pygame
import time
import threading
from collections import deque
import heapq
import math
pygame.init()


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Traffic Junction Simulator - AL2 Priority Lane")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 150, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)


paused = False
move_events = deque()
clock = pygame.time.Clock()
running = True


class Vehicle:
    def __init__(self, lane_id, vehicle_id, car_image):
        self.lane_id = lane_id
        self.vehicle_id = vehicle_id
        self.original_image = car_image
        self.image = car_image
        self.pos = list(self.get_queue_position(0))
        self.target_pos = None
        self.moving = False
        self.rotation = self.get_initial_rotation()
        self.path = []
        self.path_index = 0
        self.queue_position = 0
        
    def get_initial_rotation(self):
        """Get initial rotation based on lane direction"""
        if self.lane_id.startswith('A'):  # Coming from top
            return 180
        elif self.lane_id.startswith('B'):  # Coming from bottom
            return 0
        elif self.lane_id.startswith('C'):  # Coming from right
            return 270
        elif self.lane_id.startswith('D'):  # Coming from left
            return 90
        return 0
    
    def get_queue_position(self, queue_index):
        """Get position in queue based on lane and index"""
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        spacing = 45
        
        # Lane A 
        if self.lane_id == "AL1":
            return (center_x - 45, center_y - 150 - (queue_index * spacing))
        elif self.lane_id == "AL2":
            return (center_x, center_y - 150 - (queue_index * spacing))
        elif self.lane_id == "AL3":
            return (center_x + 45, center_y - 150 - (queue_index * spacing))
        
        # Lane B
        elif self.lane_id == "BL1":
            return (center_x + 45, center_y + 150 + (queue_index * spacing))
        elif self.lane_id == "BL2":
            return (center_x, center_y + 150 + (queue_index * spacing))
        elif self.lane_id == "BL3":
            return (center_x - 45, center_y + 150 + (queue_index * spacing))
        
        # Lane C
        elif self.lane_id == "CL1":
            return (center_x + 150 + (queue_index * spacing), center_y + 45)
        elif self.lane_id == "CL2":
            return (center_x + 150 + (queue_index * spacing), center_y)
        elif self.lane_id == "CL3":
            return (center_x + 150 + (queue_index * spacing), center_y - 45)
        
        # Lane D 
        elif self.lane_id == "DL1":
            return (center_x - 150 - (queue_index * spacing), center_y - 45)
        elif self.lane_id == "DL2":
            return (center_x - 150 - (queue_index * spacing), center_y)
        elif self.lane_id == "DL3":
            return (center_x - 150 - (queue_index * spacing), center_y + 45)
        
        return (center_x, center_y)
    
    def create_path(self, from_lane, to_lane):
        """Create curved path from source to destination"""
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        path = []
        
       
        if from_lane == "AL3" and to_lane == "CL1":
            start = (center_x + 45, center_y - 150)
            path = self.create_curve(start, (center_x + 45, center_y - 60), 
                                    (center_x + 60, center_y + 45), 90)
            for i in range(40):
                path.append((center_x + 60 + i * 10, center_y + 45))
        
 
        elif from_lane == "BL3" and to_lane == "DL1":
            start = (center_x - 45, center_y + 150)
            path = self.create_curve(start, (center_x - 45, center_y + 60),
                                    (center_x - 60, center_y - 45), 180)
            for i in range(40):
                path.append((center_x - 60 - i * 10, center_y - 45))
        

        elif from_lane == "CL3" and to_lane == "BL1":
            start = (center_x + 150, center_y - 45)
            path = self.create_curve(start, (center_x + 60, center_y - 45),
                                    (center_x + 45, center_y + 60), 0)
            for i in range(40):
                path.append((center_x + 45, center_y + 60 + i * 10))
        
        
        elif from_lane == "DL3" and to_lane == "AL1":
            start = (center_x - 150, center_y + 45)
            path = self.create_curve(start, (center_x - 60, center_y + 45),
                                    (center_x - 45, center_y - 60), 270)
            for i in range(40):
                path.append((center_x - 45, center_y - 60 - i * 10))
        
       
        elif from_lane == "AL2" and to_lane == "BL2":
            start = (center_x, center_y - 150)
            for i in range(60):
                path.append((center_x, center_y - 150 + i * 10))
        
      
        elif from_lane == "AL2" and to_lane == "DL2":
            start = (center_x, center_y - 150)
            path = self.create_curve(start, (center_x, center_y - 60),
                                    (center_x - 60, center_y), 180)
            for i in range(40):
                path.append((center_x - 60 - i * 10, center_y))
        
   
        elif from_lane == "BL2" and to_lane == "AL2":
            start = (center_x, center_y + 150)
            for i in range(60):
                path.append((center_x, center_y + 150 - i * 10))
        
        
        elif from_lane == "BL2" and to_lane == "CL2":
            start = (center_x, center_y + 150)
            path = self.create_curve(start, (center_x, center_y + 60),
                                    (center_x + 60, center_y), 0)
            for i in range(40):
                path.append((center_x + 60 + i * 10, center_y))
        
    
        elif from_lane == "CL2" and to_lane == "DL2":
            start = (center_x + 150, center_y)
            for i in range(60):
                path.append((center_x + 150 - i * 10, center_y))
        
    
        elif from_lane == "CL2" and to_lane == "AL2":
            start = (center_x + 150, center_y)
            path = self.create_curve(start, (center_x + 60, center_y),
                                    (center_x, center_y - 60), 270)
            for i in range(40):
                path.append((center_x, center_y - 60 - i * 10))
        

        elif from_lane == "DL2" and to_lane == "CL2":
            start = (center_x - 150, center_y)
            for i in range(60):
                path.append((center_x - 150 + i * 10, center_y))
        

        elif from_lane == "DL2" and to_lane == "BL2":
            start = (center_x - 150, center_y)
            path = self.create_curve(start, (center_x - 60, center_y),
                                    (center_x, center_y + 60), 90)
            for i in range(40):
                path.append((center_x, center_y + 60 + i * 10))
        
        self.path = path if path else [self.pos[:]]
        self.path_index = 0
        self.moving = True
    
    def create_curve(self, start, control, end, start_angle):
        """Create a bezier curve path"""
        path = []
        steps = 25
        for i in range(steps):
            t = i / steps
            
            x = (1-t)**2 * start[0] + 2*(1-t)*t * control[0] + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * control[1] + t**2 * end[1]
            path.append((x, y))
        return path
    
    def update_rotation_to_path(self):
        """Update rotation based on movement direction"""
        if self.path_index < len(self.path) - 1:
            current = self.path[self.path_index]
            next_pos = self.path[self.path_index + 1]
            
            dx = next_pos[0] - current[0]
            dy = next_pos[1] - current[1]
            
            
            angle = math.degrees(math.atan2(-dy, dx))
            self.rotation = (angle - 90) % 360
    
    def update(self):
        """Update vehicle position along path"""
        if self.moving and self.path and self.path_index < len(self.path):
            target = self.path[self.path_index]
            
            dx = target[0] - self.pos[0]
            dy = target[1] - self.pos[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 3:
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.moving = False
                    return True
                self.update_rotation_to_path()
            else:
                speed = 2.5  
                self.pos[0] += (dx / dist) * speed
                self.pos[1] += (dy / dist) * speed
        
        return False
    
    def draw(self, surface):
        """Draw vehicle with rotation"""
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        surface.blit(self.image, rect)


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
    
    def get_all(self):
        return self.queue[:]


class LanePriorityQueue:
    def __init__(self):
        self.heap = []
        self.counter = 0
        
    def push(self, priority, lane_group):
        heapq.heappush(self.heap, (priority, self.counter, lane_group))
        self.counter += 1
    
    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)[2]
        return None
    
    def is_empty(self):
        return len(self.heap) == 0


lane = {
    "AL1": Queue(), "AL2": Queue(), "AL3": Queue(),
    "BL1": Queue(), "BL2": Queue(), "BL3": Queue(),
    "CL1": Queue(), "CL2": Queue(), "CL3": Queue(),
    "DL1": Queue(), "DL2": Queue(), "DL3": Queue(),
}


lane_stats = {
    "AL1": {"passed": 0}, "AL2": {"passed": 0}, "AL3": {"passed": 0},
    "BL1": {"passed": 0}, "BL2": {"passed": 0}, "BL3": {"passed": 0},
    "CL1": {"passed": 0}, "CL2": {"passed": 0}, "CL3": {"passed": 0},
    "DL1": {"passed": 0}, "DL2": {"passed": 0}, "DL3": {"passed": 0},
}


visual_vehicles = {}
vehicle_id_counter = 0
last_move_time = {"A": 0, "B": 0, "C": 0, "D": 0}  

LaneA_light = LaneB_light = LaneC_light = LaneD_light = "RED"
TIME_PER_VEHICLE = 1
PRIORITY_THRESHOLD = 10

def is_priority_active():
    """Check if AL2 has priority (≥10 vehicles)"""
    return lane["AL2"].size() >= PRIORITY_THRESHOLD

def calculate_vehicles_to_serve(lanes_to_check):
    """Calculate average vehicles to serve from normal lanes"""
    if not lanes_to_check:
        return 0
    
    total_vehicles = sum(lane[l].size() for l in lanes_to_check)
    n = len(lanes_to_check)
    vehicles_to_serve = max(1, int(total_vehicles / n))
    return vehicles_to_serve

def light_changer():
    global LaneA_light, LaneB_light, LaneC_light, LaneD_light
    
    while running:
        if paused:
            time.sleep(0.2)
            continue
        
        lane_priority_queue = LanePriorityQueue()
        
        if is_priority_active():
            lane_priority_queue.push(0, "AC_PRIORITY")
        else:
            lane_priority_queue.push(1, "AC")
        
        lane_priority_queue.push(1, "BD")
        
        while not lane_priority_queue.is_empty():
            phase = lane_priority_queue.pop()
            
            if phase in ["AC", "AC_PRIORITY"]:
                LaneA_light = LaneC_light = "GREEN"
                LaneB_light = LaneD_light = "RED"
                
                if phase == "AC_PRIORITY":
                    vehicles_to_serve = lane["AL2"].size()
                    green_time = max(8, vehicles_to_serve * TIME_PER_VEHICLE)
                    print(f"[PRIORITY] AL2 has {vehicles_to_serve} vehicles")
                else:
                    normal_lanes = ["BL2", "CL2", "DL2"]
                    vehicles_to_serve = calculate_vehicles_to_serve(normal_lanes)
                    green_time = max(8, vehicles_to_serve * TIME_PER_VEHICLE)
                
                time.sleep(green_time)
                
            elif phase == "BD":
                LaneA_light = LaneC_light = "RED"
                LaneB_light = LaneD_light = "GREEN"
                
                if is_priority_active():
                    normal_lanes = ["BL3", "CL3", "DL3"]
                else:
                    normal_lanes = ["AL2", "BL3", "CL3", "DL3"]
                
                vehicles_to_serve = calculate_vehicles_to_serve(normal_lanes)
                green_time = max(8, vehicles_to_serve * TIME_PER_VEHICLE)
                
                time.sleep(green_time)

def generator():
    global vehicle_id_counter
    i = 0
    
    while running:
        if paused:
            time.sleep(0.2)
            continue
        
  
        for l in ["AL3", "BL3", "CL3", "DL3"]:
            vehicle_id = f"{l}_{vehicle_id_counter}"
            vehicle_id_counter += 1
            lane[l].enqueue(vehicle_id)
            car_img = car1_img if i % 2 == 0 else car3_img
            visual_vehicles[vehicle_id] = Vehicle(l, vehicle_id, car_img)
        
        time.sleep(5)
        
        
        for l in ["AL2", "BL2", "CL2", "DL2"]:
            vehicle_id = f"{l}_{vehicle_id_counter}"
            vehicle_id_counter += 1
            lane[l].enqueue(vehicle_id)
            car_img = car1_img if i % 2 == 0 else car3_img
            visual_vehicles[vehicle_id] = Vehicle(l, vehicle_id, car_img)
        
        i += 1
        time.sleep(5)

def traversal():
    while running:
        if paused:
            time.sleep(0.2)
            continue
        
        current_time = time.time()
        moved = False
        
    
        if LaneA_light == "GREEN" and (current_time - last_move_time["A"]) >= 1.2:
            
            if not lane["AL3"].is_empty():
                vehicle_id = lane["AL3"].dequeue()
                lane_stats["AL3"]["passed"] += 1
                if vehicle_id in visual_vehicles:
                    visual_vehicles[vehicle_id].create_path("AL3", "CL1")
                    last_move_time["A"] = current_time
            elif not lane["AL2"].is_empty():
                vehicle_id = lane["AL2"].dequeue()
                lane_stats["AL2"]["passed"] += 1
                if vehicle_id in visual_vehicles:
                    
                    import random
                    destination = random.choice(["BL2", "DL2"])
                    visual_vehicles[vehicle_id].create_path("AL2", destination)
                    last_move_time["A"] = current_time
        
        if LaneC_light == "GREEN" and (current_time - last_move_time["C"]) >= 1.2:
            if not lane["CL3"].is_empty():
                vehicle_id = lane["CL3"].dequeue()
                lane_stats["CL3"]["passed"] += 1
                if vehicle_id in visual_vehicles:
                    visual_vehicles[vehicle_id].create_path("CL3", "BL1")
                    last_move_time["C"] = current_time
            elif not lane["CL2"].is_empty():
                vehicle_id = lane["CL2"].dequeue()
                lane_stats["CL2"]["passed"] += 1
                if vehicle_id in visual_vehicles:
                    import random
                    destination = random.choice(["DL2", "AL2"])
                    visual_vehicles[vehicle_id].create_path("CL2", destination)
                    last_move_time["C"] = current_time
        
       
        if LaneB_light == "GREEN" and (current_time - last_move_time["B"]) >= 1.2:
            if not lane["BL3"].is_empty():
                vehicle_id = lane["BL3"].dequeue()
                lane_stats["BL3"]["passed"] += 1
                if vehicle_id in visual_vehicles:
                    visual_vehicles[vehicle_id].create_path("BL3", "DL1")
                    last_move_time["B"] = current_time
            elif not lane["BL2"].is_empty():
                vehicle_id = lane["BL2"].dequeue()
                lane_stats["BL2"]["passed"] += 1
                if vehicle_id in visual_vehicles:
                    import random
                    destination = random.choice(["AL2", "CL2"])
                    visual_vehicles[vehicle_id].create_path("BL2", destination)
                    last_move_time["B"] = current_time
        
        if LaneD_light == "GREEN" and (current_time - last_move_time["D"]) >= 1.2:
            if not lane["DL3"].is_empty():
                vehicle_id = lane["DL3"].dequeue()
                lane_stats["DL3"]["passed"] += 1
                if vehicle_id in visual_vehicles:
                    visual_vehicles[vehicle_id].create_path("DL3", "AL1")
                    last_move_time["D"] = current_time
            elif not lane["DL2"].is_empty():
                vehicle_id = lane["DL2"].dequeue()
                lane_stats["DL2"]["passed"] += 1
                if vehicle_id in visual_vehicles:
                    import random
                    destination = random.choice(["CL2", "BL2"])
                    visual_vehicles[vehicle_id].create_path("DL2", destination)
                    last_move_time["D"] = current_time
        
        time.sleep(0.1)


try:
    road_img = pygame.image.load("road.png")
    road_img = pygame.transform.scale(road_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    road_img = None

try:
    car1_img = pygame.image.load("car1.png")
    car1_img = pygame.transform.scale(car1_img, (25, 40))
except:
    car1_img = pygame.Surface((25, 40))
    car1_img.fill(RED)

try:
    car3_img = pygame.image.load("car3.png")
    car3_img = pygame.transform.scale(car3_img, (25, 40))
except:
    car3_img = pygame.Surface((25, 40))
    car3_img.fill(BLUE)

def draw_junction():
    """Draw the junction and roads"""
    if road_img:
        screen.blit(road_img, (0, 0))
    else:
        screen.fill((34, 139, 34))  
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
 
        pygame.draw.rect(screen, DARK_GRAY, (center_x - 70, 0, 140, SCREEN_HEIGHT))
        pygame.draw.rect(screen, DARK_GRAY, (0, center_y - 70, SCREEN_WIDTH, 140))
        
        
        for i in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, WHITE, (center_x - 45, i), (center_x - 45, i + 20), 2)
            pygame.draw.line(screen, WHITE, (center_x + 45, i), (center_x + 45, i + 20), 2)
        
       
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, WHITE, (i, center_y - 45), (i + 20, center_y - 45), 2)
            pygame.draw.line(screen, WHITE, (i, center_y + 45), (i + 20, center_y + 45), 2)
        
        
        pygame.draw.rect(screen, GRAY, (center_x - 70, center_y - 70, 140, 140))

def draw_traffic_lights():
    """Draw traffic light indicators"""
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    light_size = 20
    
  
    color = GREEN if LaneA_light == "GREEN" else RED
    pygame.draw.circle(screen, BLACK, (center_x, center_y - 120), light_size + 3)
    pygame.draw.circle(screen, color, (center_x, center_y - 120), light_size)
    
    
    color = GREEN if LaneB_light == "GREEN" else RED
    pygame.draw.circle(screen, BLACK, (center_x, center_y + 120), light_size + 3)
    pygame.draw.circle(screen, color, (center_x, center_y + 120), light_size)
    
  
    color = GREEN if LaneC_light == "GREEN" else RED
    pygame.draw.circle(screen, BLACK, (center_x + 120, center_y), light_size + 3)
    pygame.draw.circle(screen, color, (center_x + 120, center_y), light_size)
    

    color = GREEN if LaneD_light == "GREEN" else RED
    pygame.draw.circle(screen, BLACK, (center_x - 120, center_y), light_size + 3)
    pygame.draw.circle(screen, color, (center_x - 120, center_y), light_size)

def draw_info():
    """Draw simulation info"""
    font = pygame.font.Font(None, 20)
    
 
    pygame.draw.rect(screen, (0, 0, 0, 180), (10, 10, 200, 360))
    
 
    header_font = pygame.font.Font(None, 22)
    header = header_font.render("Lane Stats", True, YELLOW)
    screen.blit(header, (18, 15))
    
    y = 40
    lanes_order = ["AL1", "AL2", "AL3", "BL1", "BL2", "BL3", 
                   "CL1", "CL2", "CL3", "DL1", "DL2", "DL3"]
    
    for lane_name in lanes_order:
        waiting = lane[lane_name].size()
        passed = lane_stats[lane_name]["passed"]
        
       
        if lane_name == "AL2" and is_priority_active():
            color = YELLOW
            lane_text = f"►{lane_name}"
        else:
            color = WHITE
            lane_text = f" {lane_name}"
        
        text = font.render(f"{lane_text}: W:{waiting} P:{passed}", True, color)
        screen.blit(text, (18, y))
        y += 28
    
   
    if is_priority_active():
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 280, 10, 270, 50))
        priority_font = pygame.font.Font(None, 32)
        priority_text = priority_font.render("⚠ AL2 PRIORITY ACTIVE", True, YELLOW)
        screen.blit(priority_text, (SCREEN_WIDTH - 270, 22))
    
    
    control_font = pygame.font.Font(None, 22)
    controls = control_font.render("SPACE: Pause | ESC: Exit", True, WHITE)
    screen.blit(controls, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 30))

def update_queue_positions():
    """Update visual positions of vehicles in queues"""
    for lane_name, queue in lane.items():
        vehicles_in_queue = queue.get_all()
        for idx, vehicle_id in enumerate(vehicles_in_queue):
            if vehicle_id in visual_vehicles and not visual_vehicles[vehicle_id].moving:
                visual_vehicles[vehicle_id].queue_position = idx
                visual_vehicles[vehicle_id].pos = list(
                    visual_vehicles[vehicle_id].get_queue_position(idx)
                )


threading.Thread(target=light_changer, daemon=True).start()
threading.Thread(target=generator, daemon=True).start()
threading.Thread(target=traversal, daemon=True).start()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_ESCAPE:
                running = False
    

    update_queue_positions()
    
    
    draw_junction()
    draw_traffic_lights()
    
    vehicles_to_remove = []
    for vehicle_id, vehicle in visual_vehicles.items():
        finished = vehicle.update()
        if finished and vehicle.moving == False:
            if vehicle.path_index >= len(vehicle.path) - 1:
                vehicles_to_remove.append(vehicle_id)
        vehicle.draw(screen)
    
   
    for vid in vehicles_to_remove:
        visual_vehicles.pop(vid, None)
    
    draw_info()
    

    if paused:
        font = pygame.font.Font(None, 96)
        pause_text = font.render("⏸ PAUSED", True, YELLOW)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        pygame.draw.rect(screen, BLACK, text_rect.inflate(40, 40))
        screen.blit(pause_text, text_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Simulation ended")