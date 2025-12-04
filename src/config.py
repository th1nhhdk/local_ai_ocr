# src/config.py

APP_VERSION = "v2.0"
APP_ID = f"th1nhhdk.localaiocr.{APP_VERSION}"
APP_AUTHOR = "Nguyễn Phước Thịnh"
PROJECT_URL = "https://github.com/th1nhhdk/local_ai_ocr"

OLLAMA_HOST = "http://127.0.0.1:11435"
OLLAMA_MODEL = "deepseek-ocr:3b"

# DeepSeek-OCR / Janus expects 1024x1024 inputs
TARGET_IMAGE_SIZE = (1024, 1024)

# Configuration from vLLM-Inference example
INFERENCE_PARAMS = {
    "temperature": 0.0,
    "num_predict": 8192,
    "num_ctx": 8192,
    "repeat_last_n": 256,  # This is *4 of what VLLM uses (window_size=90).
    "repeat_penalty": 1.2, # Strongly discourage model infinite looping (It doesn't actually work).
}

PROMPTS = {
    "p_markdown": "<|grounding|>Convert the document to markdown.",
    "p_ocr":      "<|grounding|>OCR this image.",
    "p_freeocr":  "Free OCR.",
}

DEFAULT_PROMPT = "p_markdown"