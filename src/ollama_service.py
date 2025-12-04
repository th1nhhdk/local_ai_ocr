# src/ollama_service.py
# Provides functions to communicate with Ollama server.

from ollama import Client
from PySide6.QtCore import QThread, Signal
import config


def stream_ocr_response(client: Client, model_name: str, prompt: str, image_bytes: bytes, options: dict = None):
    stream = client.chat(
        model=model_name,
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_bytes]  # Pass image as raw bytes
        }],
        options=options,
        stream=True  # Enable streaming - yields chunks instead of blocking
    )

    for chunk in stream:
        # Navigate the nested response structure to extract text
        content = chunk.get('message', {}).get('content', '')
        if content:
            yield content


class ModelUnloadWorker(QThread):
    # Background thread to unload the AI model from GPU memory.
    # Runs in background because checking model status can take time.
    finished = Signal(bool, str)  # (success, message_key_or_error)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        try:
            # First, check if the model is actually loaded
            is_loaded = True
            try:
                response = self.client.ps()  # Get list of running models
                # Handle both object and dict response formats
                if hasattr(response, 'models'):
                    models = response.models
                else:
                    models = response.get('models', [])

                is_loaded = False
                for m in models:
                    # Handle both attribute and dict access
                    name = m.model if hasattr(m, 'model') else m.get('model')
                    if name == config.OLLAMA_MODEL:
                        is_loaded = True
                        break
            except Exception:
                # If ps() fails, assume model is loaded to force unload attempt
                is_loaded = True

            if is_loaded:
                # Unload by sending empty request with keep_alive=0
                # This tells Ollama to immediately unload after this request
                self.client.chat(model=config.OLLAMA_MODEL, messages=[], keep_alive=0)
                self.finished.emit(True, "msg_model_unloaded")
            else:
                self.finished.emit(True, "msg_model_not_loaded")
        except Exception as e:
            self.finished.emit(False, str(e))
