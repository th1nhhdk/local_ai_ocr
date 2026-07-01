import os
import sys
import subprocess
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QApplication
from PySide6.QtCore import QThread, Signal, Qt
import config

class DownloadWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(bool)

    def run(self):
        try:
            os.makedirs(config.MODEL_DIR, exist_ok=True)
            env = os.environ.copy()
            env["HF_HOME"] = config.MODEL_DIR

            # Use huggingface-cli
            cmd = [sys.executable, "-m", "huggingface_hub.cli.cli", "download", "Dogacel/Universal-DeepSeek-OCR-2"]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )

            for line in process.stdout:
                self.log_signal.emit(line.strip())

            process.wait()
            if process.returncode == 0:
                self.finished_signal.emit(True)
            else:
                self.finished_signal.emit(False)
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
        if text:
            # Simple carriage return handling for tqdm
            if '\r' in text:
                text = text.split('\r')[-1]
            self.log_output.append(text)
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
