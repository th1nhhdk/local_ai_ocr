# src/ocr_engine.py
from ollama import Client

def stream_ocr_response(client: Client, model_name: str, prompt: str, image_bytes: bytes):
    # Generator that yields chunks of text from Ollama.
    stream = client.chat(
        model=model_name,
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_bytes]
        }],
        # Configuration from vLLM-Inference example
        options={
            "temperature": 0.0,
            "num_predict": 8192,
            "num_ctx": 8192,
            "repeat_last_n": 256, # This is *4 of what VLLM uses (window_size=90).
            # We use 1.2 to strongly discourage model infinite looping (It doesn't acually work)
            "repeat_penalty": 1.2,
        },
        stream=True
    )

    for chunk in stream:
        content = chunk.get('message', {}).get('content', '')
        if content:
            yield content