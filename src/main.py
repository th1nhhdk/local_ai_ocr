# src/main.py
import sys
import os
import ctypes

# FIX: Add "src/" into Python's search path
# This is needed for Embeddable Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ollama import Client
from gui import OCRWindow
from constants import OLLAMA_HOST_DEFAULT

try:
    # Arbitrary unique string to group taskbar icons
    myappid = 'th1nhhdk.localaiocr.1.0.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def load_stylesheet(app):
    # Load Nord theme from style.qss
    style_path = os.path.join(current_dir, "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print("Warning: style.qss not found.")

def main():
    app = QApplication(sys.argv)
    
    # Load Theme
    load_stylesheet(app)
    
    # Set program icon
    icon_path = os.path.join(current_dir, "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # run.ps1 does set the OLLAMA_HOST variable
    host = os.environ.get("OLLAMA_HOST", OLLAMA_HOST_DEFAULT)
    client = Client(host=host)
    
    window = OCRWindow(client)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()