# src/file_handler.py
import io
import fitz  # PyMuPDF
from PIL import Image # Pillow

# Increase Pillow's limit to handle large files without warning
Image.MAX_IMAGE_PIXELS = None

def get_image_bytes(filepath):
    # Reads an image file and converts it to a standard RGB PNG byte stream.
    # This prevents issues with unsupported formats (TIFF, CMYK, etc.).
    try:
        with Image.open(filepath) as img:
            # Convert transparent backgrounds to white
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGBA')
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Export to standard PNG bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
            
    except Exception as e:
        print(f"PIL failed to load {filepath}, falling back to raw bytes: {e}")
        # Fallback for simple files if PIL fails
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

def extract_pdf_page_bytes(filepath, page_index, target_dpi=144):
    # Opens PDF, renders ONE specific page to bytes using 144 DPI (High Quality).
    # Includes safety scaling (MAX_DIM 3000) to prevent malloc errors on large pages.
    doc = fitz.open(filepath)
    page = doc.load_page(page_index)
    
    # Keep dimensions reasonable (prevent malloc errors)
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
    
    # Ensure we don't shrink to illegible sizes
    zoom = max(zoom, 0.5)
    
    # Create matrix
    matrix = fitz.Matrix(zoom, zoom)
    
    # Render to pixmap
    # Forces white background (alpha=False)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    
    # Convert to standard PNG bytes
    img_bytes = pix.tobytes("png")
    
    doc.close()
    return img_bytes