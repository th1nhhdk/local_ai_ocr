# local_ai_ocr

## Info
- `Ollama` version: `0.13.0`
- `deepseek-ocr:3b` version: `0e7b018b8a22`
- `Python` version: `3.14.0`

## Setup Ollama
```powershell
$env:OLLAMA_HOST = "127.0.0.1:11435" # Avoid port conflict
$env:OLLAMA_MODELS = Join-Path $PSScriptRoot "models"
.\ollama\ollama.exe pull deepseek-ocr:3b
echo FROM deepseek-ocr:3b > Modelfile
.\ollama\ollama.exe create deepseek-ocr:3b-q4_K_M -q q4_K_M
```

## Setup Python
- `python/python314._pth` uncomment line 5
- `.\python\python.exe -m pip install ollama PyMuPDF Pillow PySide6`