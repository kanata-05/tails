import time
import os
import math

class FPSCounter:
    def __init__(self, window_size=30):
        self.frame_times = []
        self.window_size = window_size
        self.last_frame_time = time.time()
    
    def tick(self):
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Add frame time to the window
        self.frame_times.append(frame_time)
        
        # Keep window at desired size
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        
        # Calculate FPS
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        else:
            fps = 0
        
        return fps

class PathFinder: 
    @staticmethod
    def distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    @staticmethod
    def angle(x1, y1, x2, y2):
        return math.atan2(y2 - y1, x2 - x1)

class AssetValidator:
    @staticmethod
    def validate_assets(path_config):
        missing_files = []
        
        # Check each directory
        for state, directory in path_config.items():                
            # Skip if not a state directory
            if state not in ("run", "fly", "idle", "sit"):
                continue
                
            # Check for required frame files
            from config import FRAME_COUNTS, SPRITE_CONFIG
            frame_count = FRAME_COUNTS.get(state, 4)
            
            # Check right-facing sprites
            right_prefix = SPRITE_CONFIG[state]["right"]
            for i in range(1, frame_count + 1):
                file_path = os.path.join(directory, f"{right_prefix}{i}.png")
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            # Check left-facing sprites
            left_prefix = SPRITE_CONFIG[state]["left"]
            for i in range(1, frame_count + 1):
                file_path = os.path.join(directory, f"{left_prefix}{i}.png")
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
        
        return len(missing_files) == 0, missing_files
