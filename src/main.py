# src/main.py

import sys
import os
import ctypes

# Add "src/" into Python's search path
# This is required for Embeddable Python to work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ollama import Client
from ui.main_window import MainWindow
import config

try:
    # Arbitrary unique string to group taskbar icons
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(config.APP_ID)
except ImportError:
    pass

def load_stylesheet(app):
    # Load Nord theme from style.qss
    style_path = os.path.join(current_dir, "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())

def main():
    app = QApplication(sys.argv)

    # Load Theme
    load_stylesheet(app)

    # Set program icon
    icon_path = os.path.join(current_dir, "res", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # run.ps1 does set the OLLAMA_HOST variable
    host = os.environ.get("OLLAMA_HOST", config.OLLAMA_HOST)
    client = Client(host=host)

    window = MainWindow(client)
    # We have to use the whole screen...
    window.showMaximized()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()