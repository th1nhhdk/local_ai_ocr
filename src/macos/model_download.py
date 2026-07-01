import os
import sys
import subprocess
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QApplication
from PySide6.QtCore import QThread, Signal, Qt
import config

class StreamInterceptor:
    def __init__(self, signal):
        self.signal = signal
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        while '\n' in self.buffer or '\r' in self.buffer:
            if '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
            else:
                line, self.buffer = self.buffer.split('\r', 1)

            line = line.strip()
            if line:
                self.signal.emit(line)

    def flush(self):
        pass

class DownloadWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(bool)

    def run(self):
        try:
            os.makedirs(config.MODEL_DIR, exist_ok=True)
            os.environ["HF_HOME"] = config.MODEL_DIR

            from huggingface_hub import snapshot_download

            old_stderr = sys.stderr
            sys.stderr = StreamInterceptor(self.log_signal)

            try:
                self.log_signal.emit("Starting download of Dogacel/Universal-DeepSeek-OCR-2...")
                snapshot_download(repo_id="Dogacel/Universal-DeepSeek-OCR-2", repo_type="model")
                self.finished_signal.emit(True)
            finally:
                sys.stderr = old_stderr
                
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False)

class ModelDownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading AI Model...")
        self.setFixedSize(500, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint) # Disable close button

        layout = QVBoxLayout(self)

        self.label = QLabel("Downloading DeepSeek-OCR-2 Model (6.67 GB)...\nThis is a one-time process and may take several minutes.")
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate
        layout.addWidget(self.progress)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.worker = DownloadWorker()
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def append_log(self, text):
        if text.strip():
            self.log_output.append(text.strip())
            self.log_output.verticalScrollBar().setValue(
                self.log_output.verticalScrollBar().maximum()
            )
            
    def on_finished(self, success):
        if success:
            self.progress.setRange(0, 100)
            self.progress.setValue(100)
            self.label.setText("Download complete! Starting application...")
            self.accept()
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.label.setText("Download failed. Please check your internet connection.")
            self.setWindowFlags(self.windowFlags() | Qt.WindowCloseButtonHint)
            self.show()

def check_and_download_model():
    """
    Checks if the model directory exists and has files. 
    If not, shows the download dialog.
    """
    if getattr(sys, 'frozen', False) and sys.platform == 'darwin':
        # Check if huggingface cache dir has models/Dogacel
        target_dir = os.path.join(config.MODEL_DIR, "hub", "models--Dogacel--Universal-DeepSeek-OCR-2")
        if not os.path.exists(target_dir):
            dialog = ModelDownloadDialog()
            dialog.exec()
