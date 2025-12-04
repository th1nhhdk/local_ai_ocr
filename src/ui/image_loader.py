# src/ui/image_loader.py
# Background thread for loading images without freezing the UI.

from PySide6.QtCore import QThread, Signal
import file_handler


class ImageLoaderThread(QThread):
    """
    Loads images or PDF pages in a background thread.

    Prevents UI freezes when loading large files or rendering PDF pages.
    Supports cancellation for quick switching between queue items.
    """
    image_loaded = Signal(bytes) # Emits PNG bytes when loading succeeds
    error_occurred = Signal(str) # Emits error message on failure

    def __init__(self, path, page_index, parent=None):
        super().__init__(parent)
        self.path = path
        self.page_index = page_index
        self._is_cancelled = False

    def run(self):
        try:
            if self._is_cancelled: return

            if self.page_index == -1:
                # Regular image file
                img_bytes = file_handler.get_image_bytes(self.path)
            else:
                # PDF page - page_index is 0-based
                img_bytes = file_handler.extract_pdf_page_bytes(self.path, self.page_index)

            # Only emit if not cancelled during load
            if not self._is_cancelled:
                self.image_loaded.emit(img_bytes)
        except Exception as e:
            if not self._is_cancelled:
                self.error_occurred.emit(str(e))

    def cancel(self):
        # Request cancellation - result will be discarded if still loading.
        self._is_cancelled = True
        self.wait(3000) # Wait up to 3 seconds for thread to finish
