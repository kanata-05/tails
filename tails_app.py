import time
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtWidgets import QApplication
from pynput import mouse

from sprite_manager import SpriteManager
from state_machine import TailsStateMachine, Event
from tails_widget import TailsWidget
from speech_manager import SpeechManager
from config import CANVAS_SIZE_WIDTH, CANVAS_SIZE_HEIGHT, TICK_MS

class TailsApp:
    def __init__(self, path_config):
        self._get_screen_info()
        
        self._init_components(path_config)
        
        self._setup_timers()
        
        self._setup_mouse_listener()
    
    def _get_screen_info(self):
        screen = QApplication.primaryScreen()
        full_geometry = screen.geometry()
        available_geometry = screen.availableGeometry()
        
        self.screen_width = full_geometry.width()
        self.taskbar_y = available_geometry.height()
    
    def _init_components(self, path_config):
        canvas_size = QSize(CANVAS_SIZE_WIDTH, CANVAS_SIZE_HEIGHT)
        
        self.sprite_manager = SpriteManager(path_config, canvas_size)
        
        self.state_machine = TailsStateMachine(
            self.screen_width,
            self.taskbar_y,
            CANVAS_SIZE_WIDTH,
            CANVAS_SIZE_HEIGHT
        )
        
        self.widget = TailsWidget(self.sprite_manager, self.state_machine)
        
        self.speech_manager = SpeechManager(self.widget) # Pass the widget to SpeechManager

        # Connect signals
        self.widget.state_changed.connect(self._handle_state_change)
        self.widget.request_speech_dialog.connect(self._show_speech_dialog) # New connection
        
        self.last_tick_time = time.time()
        
        # Update the initial sprite
        self.widget.update_sprite()
        self.widget.show()
    
    def _setup_timers(self):
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animation_tick)
        self.animation_timer.start(TICK_MS)
        
        self.state_timer = QTimer()
        self.state_timer.timeout.connect(self._state_tick)
        self.state_timer.start(TICK_MS)
    
    def _setup_mouse_listener(self):
        def on_click(x, y, button, pressed):
            # Only handle right mouse button presses
            if pressed and button == mouse.Button.right:
                # Calculate target position (center Tails at click point)
                target_x = x - CANVAS_SIZE_WIDTH // 2
                target_y = y - CANVAS_SIZE_HEIGHT // 2
                
                # Process right click event in state machine
                self.state_machine.process_event(
                    Event.RIGHT_CLICK, 
                    x=target_x, 
                    y=target_y
                )
                
                self.widget.update_sprite()
        
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()
    
    def _animation_tick(self):
        self.state_machine.increment_frame()
        
        self.widget.update_sprite()
    
    def _state_tick(self):
        # Calculate time elapsed since last tick
        current_time = time.time()
        dt = current_time - self.last_tick_time
        self.last_tick_time = current_time
        
        # Process tick event in state machine
        state_changed = self.state_machine.process_event(Event.TICK, dt=dt)
        
        if state_changed:
            self.widget.update_sprite()
    
    def _handle_state_change(self, state):
        current_tails_state = self.state_machine.get_state()["state"]

        if state == "sit":
            # Only allow sitting if not already sitting and not flying/circling
            if current_tails_state not in ("sit", "fly", "circle"):
                self.state_machine.process_event(Event.TIRED) # This transitions to "sit"
        elif state == "idle":
            # Allow standing if currently sitting
            if current_tails_state == "sit":
                self.state_machine.process_event(Event.RECOVERED) # This transitions to "idle"
            # If in fly or circle, stop flying/circling and go to idle
            elif current_tails_state in ("fly", "circle"):
                current_pos = self.state_machine.get_state()["position"]
                # Setting target to current position will stop movement and transition to idle
                self.state_machine.process_event(Event.RIGHT_CLICK, x=current_pos[0], y=current_pos[1])
        elif state == "fly":
            # Make Tails fly upward a bit from its current position
            current_state_data = self.state_machine.get_state()
            pos = current_state_data["position"]
            target_x = pos[0]
            target_y = pos[1] - 200  # Fly upward from current position
            self.state_machine.process_event(
                Event.RIGHT_CLICK,
                x=target_x,
                y=target_y
            )

        self.widget.update_sprite()
    
    def _show_speech_dialog(self):
        self.speech_manager.show_speech_dialog(parent=self.widget)
        self.widget.update()

    def close(self):
        # Stop timers
        self.animation_timer.stop()
        self.state_timer.stop()
        
        # Stop mouse listener
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        
        # Close widget
        self.widget.close()