import time
import math
from threading import Lock
from enum import Enum, auto

from config import (
    STATE_TRANSITIONS, WALK_INCREMENT, FLY_INCREMENT, 
    CIRCLE_DURATION, CIRCLE_RADIUS, TIREDNESS_DECREASE_RATE, 
    TIREDNESS_RECOVERY_RATE, TIRED_THRESHOLD, RECOVERY_THRESHOLD
)

class Event(Enum):
    RIGHT_CLICK = auto()
    TARGET_REACHED = auto()
    TIRED = auto()
    RECOVERED = auto()
    CIRCLE_COMPLETE = auto()
    TICK = auto()  # Regular timer tick

class TailsStateMachine:
    def __init__(self, screen_width, taskbar_y, canvas_width, canvas_height):
        self.lock = Lock()
        
        # Position state
        self.x = screen_width // 2 - canvas_width // 2  # Start in center of taskbar
        self.y = taskbar_y - canvas_height
        self.taskbar_y = taskbar_y
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        
        # Animation state
        self.current_state = "sit"  # Start sitting
        self.direction = "R"
        self.frame_index = 0
        
        # Movement state
        self.target = None
        self.circle_start_time = None
        self.circle_center = None
        
        # Tiredness state (100 = full energy, 0 = tired)
        self.tiredness = 100.0
        self.last_update_time = time.time()
    
    def process_event(self, event, **kwargs):
        with self.lock:
            old_state = self.current_state
            
            if event == Event.RIGHT_CLICK:
                # Handle right click
                target_x = kwargs.get('x')
                target_y = kwargs.get('y')
                
                if target_x is None or target_y is None:
                    return False
                
                # whether to walk or fly based on vertical distance
                vertical_distance = abs(target_y - self.y)
                new_state = "fly" if vertical_distance > 75 else "walk"
                
                self.target = (target_x, target_y)
                self.current_state = new_state
                self.circle_start_time = None
                
                # Update direction based on target
                self.direction = "L" if target_x < self.x else "R"
                
                return old_state != self.current_state
            
            elif event == Event.TICK:
                # Regular update tick
                dt = kwargs.get('dt', 0)
                return self._update_state(dt)
            
            # Let the FSM handle other events based on the current state
            next_state = self._get_next_state(event)
            if next_state != self.current_state:
                self.current_state = next_state
                # Reset frame index on state change
                self.frame_index = 0
                return True
                
            return False
    
    def _get_next_state(self, event):
        event_name = event.name.lower()
        
        # Get the transition rules for the current state
        transitions = STATE_TRANSITIONS.get(self.current_state, {})
        
        # Get the next state based on the event
        next_state = transitions.get(event_name, transitions.get("default", self.current_state))
        
        # Handle cases where the next state is a list of options
        if isinstance(next_state, list):
            # For now, we're just taking the first option
            # In a more complex implementation, we'd have logic to choose
            next_state = next_state[0]
            
        return next_state
    
    def _update_state(self, dt):
        state_changed = False
        
        # Update tiredness based on current state
        if self.current_state == "walk":
            self.tiredness = max(0, self.tiredness - TIREDNESS_DECREASE_RATE * dt)
            # Check if tired
            if self.tiredness < TIRED_THRESHOLD:
                self.current_state = "sit"
                self.frame_index = 0
                state_changed = True
        elif self.current_state == "sit":
            self.tiredness = min(100, self.tiredness + TIREDNESS_RECOVERY_RATE * (dt / 2.0))
            # Check if recovered
            if self.tiredness > RECOVERY_THRESHOLD:
                self.current_state = "idle"
                self.frame_index = 0
                state_changed = True
        
        # State-specific behavior
        if self.current_state in ("walk", "fly") and self.target:
            # Move toward target
            dx = self.target[0] - self.x
            dy = self.target[1] - self.y
            distance = math.hypot(dx, dy)
            increment = WALK_INCREMENT if self.current_state == "walk" else FLY_INCREMENT

            if distance > increment:
                # Continue moving
                angle = math.atan2(dy, dx)
                self.x += math.cos(angle) * increment
                self.y += math.sin(angle) * increment
                self.direction = "L" if dx < 0 else "R"
            else:
                # Target reached
                self.x = self.target[0]
                self.y = self.target[1]

                if self.current_state == "fly":
                    self.current_state = "circle"
                    self.circle_start_time = time.time()
                    self.circle_center = (self.x, self.y)
                    self.frame_index = 0
                    state_changed = True
                else:
                    # If target is on the ground, idle else, hover
                    if abs(self.y - (self.taskbar_y - self.canvas_height)) < 5:
                        self.current_state = "idle"
                    else:
                        self.current_state = "hover"
                    self.frame_index = 0
                    state_changed = True
                self.target = None
        
        elif self.current_state == "circle" and self.circle_start_time:
            # Perform circling behavior
            elapsed = time.time() - self.circle_start_time
            if elapsed < CIRCLE_DURATION:
                angle = (elapsed / CIRCLE_DURATION) * 2 * math.pi
                self.x = self.circle_center[0] + CIRCLE_RADIUS * math.cos(angle)
                self.y = self.circle_center[1] + CIRCLE_RADIUS * math.sin(angle)
                # Update direction based on movement
                self.direction = "L" if math.cos(angle) < 0 else "R"
            else:
                # Circle complete
                self.current_state = "idle"
                self.circle_start_time = None
                state_changed = True
        
        # Constrain vertical position ONLY for explicitly ground-based states
        if self.current_state in ("walk", "sit", "idle"):
            self.y = self.taskbar_y - self.canvas_height
        elif self.current_state == "idle":
            # Only snap to ground if already on ground (prevents teleport after flying)
            if abs(self.y - (self.taskbar_y - self.canvas_height)) < 5:
                self.y = self.taskbar_y - self.canvas_height
        
        return state_changed
    
    def get_state(self):
        """
        Get the current state information.
        
        Returns:
            dict: Current state information
        """
        with self.lock:
            display_state = self.current_state
            if self.current_state == "circle":
                display_state = "fly"
            if self.current_state == "hover":
                display_state = "idle"  # Use idle animation for hover, or create a hover sprite
            return {
                "state": display_state,
                "direction": self.direction,
                "frame_index": self.frame_index,
                "position": (int(self.x), int(self.y)),
                "tiredness": self.tiredness
            }
    
    def increment_frame(self):
        with self.lock:
            self.frame_index += 1