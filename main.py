import sys
import os
from PyQt5.QtWidgets import QApplication
import ctypes 
import platform

from tails_app import TailsApp
from config import PATH_CONFIG

if __name__ == "__main__":
    if platform.system() == "Windows":
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            print(f"Error checking admin status: {e}")
            is_admin = False # Assume not admin if check fails

        if not is_admin:
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit(0)
            except Exception as e:
                print(f"Failed to elevate privileges: {e}.")

    # Only set DPI awareness on Windows (although it's not needed, atleast on my laptop.)
    if platform.system() == "Windows":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    try:
        tails = TailsApp(PATH_CONFIG)
        print("This is the console for Tails, do not close this.")
    except Exception as e:
        print(e)
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred during application execution: {e}")
        sys.exit(1)

