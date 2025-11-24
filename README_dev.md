# Local AI OCR (v1.5)

## Tech Stack
- **Python:** Embeddable Python (`3.14.0`)
- **Ollama:** `0.13.0`
- **deepseek-ocr:3b:** `0e7b018b8a22`
- **Frontend:** PySide6 (Qt6)

## Environment setup

### Automated
- Execute `env_setup.bat`.

### Manual
1. **Python:**
   - Download [Python 3.13.9 Embeddable (Windows x64)](https://www.python.org/ftp/python/3.13.9/python-3.13.9-embed-amd64.zip).
   - Extract to `python/`.
   - Edit `python/python313._pth`: Uncomment line 5: `import site`.

2. **pip + requirements:**
   - Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py).
     ```powershell
     .\python\python.exe get-pip.py
     .\python\python.exe -m pip install -r requirements.txt
     ```

3. **DeepSeek-OCR Model:**
   ```powershell
   $env:OLLAMA_HOST = "127.0.0.1:11435" # Avoid port conflict
   $env:OLLAMA_MODELS = Join-Path $PSScriptRoot "models"
   .\ollama\ollama.exe pull deepseek-ocr:3b
   ```

## Running
- **With GPU (If possible):** `run.bat`
- **CPU-Only Mode:** `run_cpu-only.bat`