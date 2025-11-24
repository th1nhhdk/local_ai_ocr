# src/worker.py
import time
from PySide6.QtCore import QThread, Signal
from ocr_engine import stream_ocr_response
import file_handler

class OCRWorker(QThread):
    stream_chunk = Signal(str)
    image_started = Signal(str)
    image_finished = Signal(float)
    finished_all = Signal()
    error_occurred = Signal(str)

    def __init__(self, client, queue_items, prompt, model_name):
        super().__init__()
        self.client = client
        self.queue_items = queue_items 
        self.prompt = prompt
        self.model_name = model_name
        self.is_running = True 

    def run(self):
        try:
            for display_name, filepath, page_index in self.queue_items:
                if not self.is_running: break 

                self.image_started.emit(f"\n--- Processing: {display_name} ---\n")

                start_time = time.time()
                try:
                    if page_index == -1:
                        # It's a image file
                        img_bytes = file_handler.get_image_bytes(filepath)
                    else:
                        # It's a PDF page
                        img_bytes = file_handler.extract_pdf_page_bytes(filepath, page_index)
                except Exception as e:
                    self.error_occurred.emit(f"Failed to load {display_name}: {e}")
                    continue

                for chunk in stream_ocr_response(self.client, self.model_name, self.prompt, img_bytes):
                    if not self.is_running: break 
                    self.stream_chunk.emit(chunk)

                duration = time.time() - start_time

                # Explicitly delete bytes to free RAM immediately
                del img_bytes 

                if not self.is_running: break
                self.image_finished.emit(duration)

            self.finished_all.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False