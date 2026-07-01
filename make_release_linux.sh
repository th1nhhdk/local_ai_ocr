#!/usr/bin/env bash
set -e

VERSION="v3.0.0"
ARCHIVE_NAME="local_ai_ocr-${VERSION}-linux.tar.gz"

if [ -f "$ARCHIVE_NAME" ]; then
    echo "Removing existing archive: $ARCHIVE_NAME"
    rm "$ARCHIVE_NAME"
fi

echo "Creating $ARCHIVE_NAME..."

tar --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    -czvf "$ARCHIVE_NAME" \
    demo/ \
    src/ \
    .gitignore \
    env_setup_linux.sh \
    run_linux.sh \
    run_linux_cpu-only.sh \
    LICENSE \
    README.md \
    README_dev.md \
    README_en.md \
    requirements.txt

echo ""
echo "DONE: $ARCHIVE_NAME created successfully"
echo ""
