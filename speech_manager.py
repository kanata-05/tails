from PyQt5.QtWidgets import QInputDialog, QLineEdit

class SpeechManager:
    
    def __init__(self, widget):
        self.widget = widget
        self.current_text = None
    
    def show_speech_dialog(self, parent=None):
        # Ask what should tails say :3
        text, ok = QInputDialog.getText(
            parent or self.widget,
            "Tails Speech",
            "What should Tails say?",
            QLineEdit.Normal,
            ""
        )
        
        if ok and text:
            self.speak(text)
            return True
        
        return False
    
    def speak(self, text, duration=5000):
        self.current_text = text
        
        formatted_text = self._format_text(text)
        
        self.widget.set_speech(formatted_text, duration)
    
    def _format_text(self, text):
        if len(text) > 100:
            # cut and add cliff hanger
            text = text[:97] + "..."
        
        # Add smart line breaks
        
        return text
    
    def clear_speech(self):
        self.current_text = None
        self.widget.set_speech(None)
