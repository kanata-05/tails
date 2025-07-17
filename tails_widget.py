import math
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QInputDialog, QLineEdit 
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QFontMetrics
import gemini_manager as gem

from state_machine import Event

class TailsWidget(QWidget):
    # Signal to notify about state changes
    state_changed = pyqtSignal(str)
    
    def __init__(self, sprite_manager, state_machine, gem):
        super().__init__()
        self.sprite_manager = sprite_manager
        self.state_machine = state_machine
        self.gemini_manager = gem
        self.current_sprite = None
        
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
        
        sit_action = QAction("Sit", self)
        sit_action.triggered.connect(lambda: self._set_state("sit"))
        
        idle_action = QAction("Stand", self)
        idle_action.triggered.connect(lambda: self._set_state("idle"))
        
        fly_action = QAction("Fly", self)
        fly_action.triggered.connect(lambda: self._set_state("fly"))

        talk_action = QAction("Talk", self)
        talk_action.triggered.connect(self.gemini_manager.chat)
        
        self.context_menu.addAction(sit_action)
        self.context_menu.addAction(idle_action)
        self.context_menu.addAction(fly_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(talk_action)
        self.context_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.context_menu.addAction(exit_action)
    
    def _set_state(self, state):
        self.state_changed.emit(state)

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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        painter.drawPixmap(0, 0, self.current_sprite)
        painter.end()
    
    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())
        
        event.accept()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            pass
        else:
            super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        # For future implementation
        super().mouseDoubleClickEvent(event)