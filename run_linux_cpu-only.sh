#!/usr/bin/env bash

SCRIPTROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_BIN="$SCRIPTROOT/python/bin/python3"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "FATAL: Isolated Python not found. Please run ./env_setup_linux.sh first."
    exit 1
fi

export HF_HOME="$SCRIPTROOT/models"

# Disable GPUs
export CUDA_VISIBLE_DEVICES="-1"
export ROCR_VISIBLE_DEVICES="-1"
export GGML_VK_VISIBLE_DEVICES="-1"

echo "Starting Local AI OCR (CPU-Only)..."
"$PYTHON_BIN" "$SCRIPTROOT/src/main.py"
