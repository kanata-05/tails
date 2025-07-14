import math
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QInputDialog, QLineEdit 
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QFontMetrics

from state_machine import Event

class TailsWidget(QWidget):
    # Signal to notify about state changes
    state_changed = pyqtSignal(str)
    # New signal to request speech dialog from application
    request_speech_dialog = pyqtSignal()
    
    def __init__(self, sprite_manager, state_machine):
        super().__init__()
        self.sprite_manager = sprite_manager
        self.state_machine = state_machine
        self.current_sprite = None
        self.speech_text = None
        self.speech_timer = None
        self.speech_text_pixmap = None
        
        self._setup_widget()
        self._setup_context_menu()
    
    def _setup_widget(self):
        # Set window flags for frameless, always-on-top behavior
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        # Enable transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def _setup_context_menu(self):
        self.context_menu = QMenu(self)
        
        # Add actions for different states
        sit_action = QAction("Sit", self)
        sit_action.triggered.connect(lambda: self._set_state("sit"))
        
        idle_action = QAction("Stand", self)
        idle_action.triggered.connect(lambda: self._set_state("idle"))
        
        fly_action = QAction("Fly", self)
        fly_action.triggered.connect(lambda: self._set_state("fly"))
        
        # Add a separator
        self.context_menu.addAction(sit_action)
        self.context_menu.addAction(idle_action)
        self.context_menu.addAction(fly_action)
        self.context_menu.addSeparator()
        
        # Add speak action
        speak_action = QAction("Speak...", self)
        # Connect to the new signal
        speak_action.triggered.connect(self.request_speech_dialog.emit)
        self.context_menu.addAction(speak_action)
        
        # Add exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.context_menu.addAction(exit_action)
    
    def _set_state(self, state):
        # This will be handled by the application
        self.state_changed.emit(state)
    
    def _show_speak_dialog(self):
        # This method is now handled by the signal to TailsApp.
        # This empty implementation is kept to satisfy previous connections if any,
        # but the primary logic is now in TailsApp via request_speech_dialog.emit.
        pass
    
    def set_speech(self, text, duration=5000):
        self.speech_text = text
        self.speech_text_pixmap = None # Clear cached pixmap so it's re-rendered

        # Clear any existing timer
        if self.speech_timer is not None:
            self.speech_timer.stop()
        
        # Set timer to clear speech
        if text: # Only start timer if there's text to display
            self.speech_timer = QTimer(self)
            self.speech_timer.timeout.connect(self._clear_speech)
            self.speech_timer.setSingleShot(True)
            self.speech_timer.start(duration)
        
        self.update()
    
    def _clear_speech(self):
        self.speech_text = None
        self.speech_text_pixmap = None
        self.update()
    
    def update_sprite(self):
        state = self.state_machine.get_state()
        self.current_sprite = self.sprite_manager.get_sprite(
            state["state"], 
            state["direction"], 
            state["frame_index"]
        )
        self.move(*state["position"])
        self.resize(self.current_sprite.size())
        self.update()
    
    def paintEvent(self, event):
        if not self.current_sprite:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Draw the current sprite
        painter.drawPixmap(0, 0, self.current_sprite)
        
        # Draw speech bubble if needed
        if self.speech_text and self.sprite_manager.get_bubble():
            bubble = self.sprite_manager.get_bubble()
            
            # Position the bubble above Tails
            bubble_x = (self.width() - bubble.width()) // 2
            bubble_y = -bubble.height()
            
            # Draw the bubble
            painter.drawPixmap(bubble_x, bubble_y, bubble)
            
            # Draw the text inside the bubble
            painter.setPen(Qt.black)
            bubble_text_rect = bubble.rect().adjusted(10, 10, -10, -10)
            bubble_text_rect.translate(bubble_x, bubble_y)
            
            # Render text to a pixmap once for performance if it's long
            if not self.speech_text_pixmap:
                temp_pixmap = QPixmap(bubble_text_rect.size())
                temp_pixmap.fill(Qt.transparent)
                temp_painter = QPainter(temp_pixmap)
                temp_painter.setPen(Qt.black)
                temp_painter.drawText(
                    temp_pixmap.rect(),
                    Qt.AlignCenter | Qt.TextWordWrap,
                    self.speech_text
                )
                temp_painter.end()
                self.speech_text_pixmap = temp_pixmap
            
            painter.drawPixmap(bubble_text_rect.topLeft(), self.speech_text_pixmap)

        painter.end()
    
    def contextMenuEvent(self, event):
        # Show the context menu
        self.context_menu.exec_(event.globalPos())
        
        # Prevent default context menu
        event.accept()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # This event will be handled by the mouse listener in the main application
            pass
        else:
            # Let the event propagate
            super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        # For future implementation
        super().mouseDoubleClickEvent(event)