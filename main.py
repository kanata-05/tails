import sys
import ctypes
from PyQt5.QtWidgets import QApplication

from tails_app import TailsApp
from config import PATH_CONFIG

if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
    
    app = QApplication(sys.argv)
    
    tails = TailsApp(PATH_CONFIG)
    
    sys.exit(app.exec_())
