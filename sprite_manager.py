import os
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QSize

from config import FRAME_COUNTS, SPRITE_CONFIG

class SpriteManager:    
    def __init__(self, path_config, canvas_size):
        self.path_config = path_config
        self.canvas_size = canvas_size
        self.sprites = {}
        
        # Define frame file mappings based on actual filenames
        self.frame_mappings = {
            # Right-facing animations
            "run_R": [f"tailsRun{i}.png" for i in range(1, FRAME_COUNTS.get("run", 4) + 1)],
            "walk_R": [f"tailsRun{i}.png" for i in range(1, FRAME_COUNTS.get("run", 4) + 1)],  # Alias for run
            "idle_R": [f"tailsIdle{i}.png" for i in range(1, FRAME_COUNTS.get("idle", 4) + 1)],
            "fly_R": [f"tailsFly{i}.png" for i in range(1, FRAME_COUNTS.get("fly", 4) + 1)],
            "sit_R": [f"tailsSit{i}.png" for i in range(1, FRAME_COUNTS.get("sit", 4) + 1)],
            
            # Left-facing animations
            "run_L": [f"tailsRunB{i}.png" for i in range(1, FRAME_COUNTS.get("run", 4) + 1)],
            "walk_L": [f"tailsRunB{i}.png" for i in range(1, FRAME_COUNTS.get("run", 4) + 1)],  # Alias for run
            "idle_L": [f"tailsIdleB{i}.png" for i in range(1, FRAME_COUNTS.get("idle", 4) + 1)],
            "fly_L": [f"tailsFlyB{i}.png" for i in range(1, FRAME_COUNTS.get("fly", 4) + 1)],
            "sit_L": [f"tailsSitB{i}.png" for i in range(1, FRAME_COUNTS.get("sit", 4) + 1)]
        }
        
        self._load_all_sprites()
    
    def _load_all_sprites(self):
        # Load each animation state based on frame mappings
        for key, frame_files in self.frame_mappings.items():
            anim_type = key.split('_')[0]  # Extract animation type from key
            direction = key.split('_')[1]  # Extract direction from key
            
            # Use run for walk
            directory_type = "run" if anim_type == "walk" else anim_type
            
            if directory_type in self.path_config:
                directory = self.path_config[directory_type]
                self.sprites[key] = self._load_frames_from_list(
                    directory, 
                    frame_files,
                    self._get_y_offset_func(directory_type)
                )
    
    def _load_frames_from_list(self, directory, frame_files, y_offset_func):
        frames = []
        for filename in frame_files:
            file_path = os.path.join(directory, filename)
            
            if not os.path.exists(file_path):
                print(f"Warning: Frame {file_path} not found")
                continue
            
            pixmap = QPixmap(file_path)
            
            canvas = QPixmap(self.canvas_size)
            canvas.fill(Qt.transparent)
            
            painter = QPainter(canvas)
            x = (self.canvas_size.width() - pixmap.width()) // 2
            y = y_offset_func(self.canvas_size.height(), pixmap.height())
            painter.drawPixmap(x, y, pixmap)
            painter.end()
            
            frames.append(canvas)
        
        return frames
    
    def _get_y_offset_func(self, animation_type):
        if animation_type == "walk":
            animation_type = "run"
            
        if animation_type == "fly":
            return lambda H, h: (H - h) // 2  # Center vertically
        else:
            return lambda H, h: H - h  # Align to bottom
    
    def get_sprite(self, state, direction, frame_index):
        key = f"{state}_{direction}"
        
        if key not in self.sprites:
            print(f"Warning: Sprite set {key} not found")
            fallback = QPixmap(self.canvas_size)
            fallback.fill(Qt.transparent)
            return fallback
        
        frames = self.sprites[key]
        
        if state == "sit" and frame_index >= len(frames):
            # After the first complete loop, only use frames 5-10 for sitting
            # (indexes 4 to 9)
            frame_index = ((frame_index - 4) % 6) + 4
        else:
            frame_index = frame_index % len(frames)
        
        return frames[frame_index]
    