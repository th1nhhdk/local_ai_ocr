#!/usr/bin/env bash

SCRIPTROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_BIN="$SCRIPTROOT/python/bin/python3"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "FATAL: Isolated Python not found. Please run ./env_setup_linux.sh first."
    exit 1
fi

export HF_HOME="$SCRIPTROOT/models"

echo "Starting Local AI OCR..."
"$PYTHON_BIN" "$SCRIPTROOT/src/main.py"
