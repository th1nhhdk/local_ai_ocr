$PYTHON_BIN = Join-Path $PSScriptRoot "python\python.exe"
$OLLAMA_BIN = Join-Path $PSScriptRoot "ollama\ollama.exe"

$env:OLLAMA_HOST = "http://127.0.0.1:11435" # Avoid port conflict
$env:OLLAMA_MODELS = Join-Path $PSScriptRoot "models"

Write-Host "Starting Ollama..."
Start-Process -FilePath $OLLAMA_BIN -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 3

Write-Host "Downloading deepseek-ocr:3b fp16..."
& $OLLAMA_BIN pull deepseek-ocr:3b

# Ollama cleanup
Get-Process "ollama" -ErrorAction SilentlyContinue | Stop-Process -Force