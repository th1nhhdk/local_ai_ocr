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

# Output directory for temporary images and crops
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

# DeepSeek-OCR-2 Prompts
PROMPTS = {
    "p_markdown": "<image>\n<|grounding|>Convert the document to markdown.",
    "p_freeocr":  "<image>\nFree OCR.",
}

DEFAULT_PROMPT = "p_markdown"