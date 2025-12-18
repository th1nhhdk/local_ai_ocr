# src/config.py
import sys

APP_VERSION = "v2.1.1"
APP_AUTHOR = "Nguyễn Phước Thịnh"
PROJECT_URL = "https://github.com/th1nhhdk/local_ai_ocr"

# Windows-specific feature
WIN_TASKBAR_PROGRESS_SUPPORT = sys.platform == "win32"
APP_ID = f"th1nhhdk.localaiocr.{APP_VERSION}"

OLLAMA_HOST = "http://127.0.0.1:11435"
OLLAMA_MODEL = "deepseek-ocr:3b"

# Used in src/ui/{control_panel,main_window}.py
# Supported file extensions for Adding files and Drag and drop
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.heic', '.heif'}

# Configuration from Ollama Modelfile
INFERENCE_PARAMS = {
    "temperature": 0,
}

PROMPTS = {
    "p_markdown": "<|grounding|>Convert the document to markdown.",
    "p_freeocr":  "Free OCR.",
    "p_ocr":      "<|grounding|>OCR this image.",
}

DEFAULT_PROMPT = "p_markdown"