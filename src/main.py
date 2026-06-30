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
from ui.main_window import MainWindow
import config

# Windows-specific feature: Set AppUserModelID to group taskbar icons
if config.WIN_TASKBAR_PROGRESS_SUPPORT:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(config.APP_ID)

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

    window = MainWindow()
    # We have to use the whole screen...
    window.showMaximized()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()