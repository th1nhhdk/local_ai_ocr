# src/config.py
import sys
import os

APP_VERSION = "v3.0.0"
APP_AUTHOR = "Nguyễn Phước Thịnh"
PROJECT_URL = "https://github.com/th1nhhdk/local_ai_ocr"

# Windows-specific feature
WIN_TASKBAR_PROGRESS_SUPPORT = sys.platform == "win32"
APP_ID = f"th1nhhdk.localaiocr.{APP_VERSION}"

# Used in src/ui/{control_panel,main_window}.py
# Supported file extensions for Adding files and Drag and drop
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.heic', '.heif'}

# Determine base directory
if getattr(sys, 'frozen', False):
    # PyInstaller bundle
    if sys.platform == 'darwin':
        # macOS Application Support
        BASE_DIR = os.path.expanduser("~/Library/Application Support/Local AI OCR")
    else:
        # Windows/Linux PyInstaller bundle
        BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running from source
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Output directory for temporary images and crops
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Models directory
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.environ["HF_HOME"] = MODEL_DIR

# DeepSeek-OCR-2 Prompts
PROMPTS = {
    "p_markdown": "<image>\n<|grounding|>Convert the document to markdown.",
    "p_freeocr":  "<image>\nFree OCR.",
}

DEFAULT_PROMPT = "p_markdown"