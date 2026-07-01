#!/usr/bin/env bash
set -e

SCRIPTROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_DIR="$SCRIPTROOT/python"
MODEL_DIR="$SCRIPTROOT/models"

PYTHON_URL_X86="https://github.com/astral-sh/python-build-standalone/releases/download/20240726/cpython-3.13.0+20240726-x86_64-unknown-linux-gnu-install_only.tar.gz"
PYTHON_URL_AARCH64="https://github.com/astral-sh/python-build-standalone/releases/download/20240726/cpython-3.13.0+20240726-aarch64-unknown-linux-gnu-install_only.tar.gz"

FLASH_ATTN_URL_X86="https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.9.17/flash_attn-2.8.3+cu130torch2.12-cp313-cp313-linux_x86_64.whl"
FLASH_ATTN_URL_AARCH64="https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.9.22/flash_attn-2.8.3+cu130torch2.12-cp313-cp313-linux_aarch64.whl"

ARCH=$(uname -m)

echo "[1/3] Downloading Standalone Python 3.13..."
if [ -d "$PYTHON_DIR" ] && [ -f "$PYTHON_DIR/bin/python3" ]; then
    echo "- Python found in $PYTHON_DIR. Skipping download."
else
    echo "- Python missing. Starting download..."
    if [ "$ARCH" = "x86_64" ]; then
        curl -# -L -o python_standalone.tar.gz "$PYTHON_URL_X86"
    elif [ "$ARCH" = "aarch64" ]; then
        curl -# -L -o python_standalone.tar.gz "$PYTHON_URL_AARCH64"
    else
        echo "FATAL: Unsupported architecture: $ARCH"
        exit 1
    fi
    echo "- Extracting Python..."
    mkdir -p "$PYTHON_DIR"
    tar -xzf python_standalone.tar.gz -C "$PYTHON_DIR" --strip-components=1
    rm python_standalone.tar.gz
fi

PYTHON_BIN="$PYTHON_DIR/bin/python3"

echo "[2/3] Installing Requirements..."
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install torch==2.12.1 torchvision==0.27.1 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cu130

echo "- Installing Flash Attention 2 for Python 3.13..."
if [ "$ARCH" = "x86_64" ]; then
    "$PYTHON_BIN" -m pip install "$FLASH_ATTN_URL_X86" || echo "Warning: Failed to install flash-attn wheel. Continuing anyway..."
elif [ "$ARCH" = "aarch64" ]; then
    "$PYTHON_BIN" -m pip install "$FLASH_ATTN_URL_AARCH64" || echo "Warning: Failed to install flash-attn wheel. Continuing anyway..."
fi

echo "- Installing other requirements..."
"$PYTHON_BIN" -m pip install -r "$SCRIPTROOT/requirements.txt"

echo "[3/3] Downloading DeepSeek-OCR-2 Model..."
mkdir -p "$MODEL_DIR"
export HF_HOME="$MODEL_DIR"
"$PYTHON_DIR/bin/huggingface-cli" download Dogacel/Universal-DeepSeek-OCR-2 || { echo "FATAL: Model download failed."; exit 1; }

echo ""
echo "INFO: Environment setup complete."
echo "You can now run './run_linux.sh' or './run_linux_cpu-only.sh'."
