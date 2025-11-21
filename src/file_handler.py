# src/file_handler.py
import os
import fitz  # PyMuPDF

def get_image_bytes(filepath):
    # Reads a standard image file directly.
    with open(filepath, "rb") as f:
        return f.read()

def get_pdf_page_count(filepath):
    # Returns the number of pages in a PDF without loading images.
    try:
        doc = fitz.open(filepath)
        count = len(doc)
        doc.close()
        return count
    except:
        return 0

def extract_pdf_page_bytes(filepath, page_index):
    # Opens PDF, renders ONE specific page to bytes, and closes PDF.
    # This ensures minimal RAM usage.
    # Also includes safety scaling to prevent malloc errors on huge pages.
    doc = fitz.open(filepath)
    page = doc.load_page(page_index)

    # Target max dimension
    # 3500 Causes freeze, 2000 causes infinite looping
    MAX_DIM = 3000

    rect = page.rect
    width, height = rect.width, rect.height

    # 2x zoom is usually good enough for standard documents
    zoom = 2.0

    # If 2x zoom would create a huge image, scale it DOWN instead
    if (width * zoom > MAX_DIM) or (height * zoom > MAX_DIM):
        zoom = MAX_DIM / max(width, height)

    # Ensure we don't shrink it to much (min 0.5x)
    zoom = max(zoom, 0.5)

    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes