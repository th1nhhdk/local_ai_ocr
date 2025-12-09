# src/file_handler.py
# Handles loading and preprocessing of images and PDF files for OCR.

import io
import fitz # PyMuPDF
from PIL import Image # Pillow
import pillow_heif # Handle HEIC images
import config

# Register HEIC opener
pillow_heif.register_heif_opener()

# Disable Pillow's safety limit for very large images (e.g. scanned documents)
Image.MAX_IMAGE_PIXELS = None


# Ollama already handled the image padding
# See: https://github.com/ollama/ollama/blob/main/model/models/deepseekocr/imageprocessor.go
def preprocess_image(img: Image.Image) -> bytes:
    # Apply standard preprocessing (transparency handling) and return PNG bytes.
    # We DO NOT resize or pad here because Ollama needs the original
    # high-resolution image to perform its own multi-view cropping.

    # Flatten transparent alpha channel onto white background
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        img = img.convert('RGBA')
        background = Image.new('RGB', img.size, (255, 255, 255))
        # img.split()[-1] extracts the alpha channel as a mask
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Export as PNG bytes (lossless format preserves text quality)
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    return img_buffer.getvalue()

def get_image_bytes(filepath):
    # Read an image file, preprocess it, and return PNG bytes.
    try:
        with Image.open(filepath) as img:
            return preprocess_image(img)
    except Exception as e:
        print(f"PIL failed to load {filepath} or process it: {e}")
        # Fallback: return raw file bytes if preprocessing fails
        with open(filepath, "rb") as f:
            return f.read()

def get_pdf_page_count(filepath):
    # Return the number of pages in a PDF without loading images.
    try:
        doc = fitz.open(filepath)
        count = len(doc)
        doc.close()
        return count
    except Exception as e:
        print(f"Failed to get PDF page count for {filepath}: {e}")
        return 0

def extract_pdf_page_bytes(filepath, page_index, target_dpi=144):
    # Render a PDF page as an image, preprocess it, and return PNG bytes.
    doc = fitz.open(filepath)
    page = doc.load_page(page_index)

    # Cap maximum dimension to prevent malloc errors
    # 3500 Causes long freeze, 2000 causes infinite looping
    MAX_DIM = 3000
    rect = page.rect
    width, height = rect.width, rect.height

    # Calculate zoom based on DPI
    # 144 / 72.0 (Default PDF DPI) = 2.0x zoom.
    zoom = target_dpi / 72.0

    # If 144 DPI results in a huge image (>3000px), scale down to fit MAX_DIM.
    if (width * zoom > MAX_DIM) or (height * zoom > MAX_DIM):
        zoom = MAX_DIM / max(width, height)
    zoom = max(zoom, 0.5)  # Minimum 50% zoom to ensure readability

    # fitz.Matrix applies uniform scaling in both dimensions
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)

    # Convert PyMuPDF pixmap to PIL Image, then preprocess
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_bytes = preprocess_image(img)

    doc.close()
    return img_bytes