# src/config.py
import sys
import os
import tomllib

APP_VERSION = "v2.2"
APP_AUTHOR = "Nguyễn Phước Thịnh"
PROJECT_URL = "https://github.com/th1nhhdk/local_ai_ocr"

# Windows-specific feature
WIN_TASKBAR_PROGRESS_SUPPORT = sys.platform == "win32"
APP_ID = f"th1nhhdk.localaiocr.{APP_VERSION}"

# Path to user config (./src/../config.toml)
CONFIG_TOML_PATH = os.path.join(os.path.dirname(__file__), "..", "config.toml")

# Default values
DEFAULT_OLLAMA_IP = "http://127.0.0.1"
DEFAULT_OLLAMA_PORT = "11435"
DEFAULT_OLLAMA_MODEL = "deepseek-ocr:3b"


def load_user_config():
    # Load configuration from TOML file. Returns dict with engine settings.
    # If file is missing or invalid, creates/resets it with defaults.
    defaults = {
        "ip_address": DEFAULT_OLLAMA_IP,
        "port": DEFAULT_OLLAMA_PORT,
        "model": DEFAULT_OLLAMA_MODEL,
    }

    try:
        with open(CONFIG_TOML_PATH, "rb") as f:
            data = tomllib.load(f)
            engine = data.get("engine", {})
            return {
                "ip_address": engine.get("ip_address", defaults["ip_address"]),
                "port": engine.get("port", defaults["port"]),
                "model": engine.get("model", defaults["model"]),
            }
    except FileNotFoundError:
        save_user_config(defaults["ip_address"], defaults["port"], defaults["model"])
        return defaults
    except tomllib.TOMLDecodeError:
        save_user_config(defaults["ip_address"], defaults["port"], defaults["model"])
        return defaults

def save_user_config(ip_address: str, port: str, model: str):
    # Save configuration to TOML file.
    content = f"""[engine]
ip_address = "{ip_address}"
port = "{port}"
model = "{model}"
"""
    with open(CONFIG_TOML_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def reload_config():
    # Reload OLLAMA_HOST and OLLAMA_MODEL from config file.
    global OLLAMA_HOST, OLLAMA_MODEL
    cfg = load_user_config()
    OLLAMA_HOST = f"{cfg['ip_address']}:{cfg['port']}"
    OLLAMA_MODEL = cfg["model"]


# Initialize from config file
_cfg = load_user_config()
OLLAMA_HOST = f"{_cfg['ip_address']}:{_cfg['port']}"
OLLAMA_MODEL = _cfg["model"]

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