# src/ui/main_window.py
# Main application window - orchestrates all panels and processing.

import time
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QSplitter, QComboBox,
                               QMessageBox, QDialog, QDialogButtonBox, QLayout,
                               QGroupBox)
from PySide6.QtCore import Qt, Slot, QUrl, QTimer
from PySide6.QtGui import QDesktopServices, QIcon

import config
import lang_handler
from ocr_worker import OCRWorker
from ollama_service import ModelUnloadWorker
from .control_panel import ControlPanel
from .output_panel import OutputPanel
from win_taskbar import TaskbarProgress


class MainWindow(QMainWindow):
    # ==================== Initialization ====================
    def __init__(self, ollama_client):
        super().__init__()
        self.client = ollama_client

        self.setWindowTitle(f"Local AI OCR ({config.APP_VERSION})")
        self.resize(1067, 600) # Six-seven... Six-seven... Six-seven...

        self.taskbar = TaskbarProgress() # Windows taskbar progress indicator

        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "res", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.current_lang_code = lang_handler.get_default_language()
        self.t = lang_handler.load_language(self.current_lang_code)

        self.worker = None # OCR worker thread
        self.unload_worker = None # Model unload worker thread
        self.batch_start_time = 0.0
        self._first_show_done = False

        self.init_ui()
        self.apply_language()

    # ==================== Lifecycle ====================
    def showEvent(self, event):
        super().showEvent(event)
        if not self._first_show_done:
            self._first_show_done = True
            # Delay GL init to after window is fully visible
            QTimer.singleShot(0, self.force_gl_init)

    def force_gl_init(self):
        # HACK: Force WebEngine GL context initialization on startup.
        # Prevents visual flicker when first switching to fancy output tab.
        self.output_panel.tabs.setCurrentIndex(1)
        QTimer.singleShot(0, lambda: self.output_panel.tabs.setCurrentIndex(0))

    # ==================== UI Layout ====================
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # === Top Bar ===
        top_bar = QHBoxLayout()

        self.btn_about = QPushButton()
        self.btn_about.clicked.connect(self.show_about)
        top_bar.addWidget(self.btn_about)

        self.btn_unload = QPushButton()
        self.btn_unload.clicked.connect(self.unload_model)
        top_bar.addWidget(self.btn_unload)

        top_bar.addStretch()

        # Select Mode (Prompt)
        self.lbl_prompt = QLabel("Select Mode:")
        self.combo_prompts = QComboBox()
        self.combo_prompts.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        top_bar.addWidget(self.lbl_prompt)
        top_bar.addWidget(self.combo_prompts)

        # Language
        top_bar.addWidget(QLabel("Language:"))
        self.combo_lang = QComboBox()
        self.languages = lang_handler.get_available_languages()
        self.combo_lang.addItems(self.languages.keys())

        display_name = next((k for k, v in self.languages.items() if v == self.current_lang_code), "English")
        self.combo_lang.setCurrentText(display_name)
        self.combo_lang.currentTextChanged.connect(self.change_language)
        top_bar.addWidget(self.combo_lang)

        main_layout.addLayout(top_bar)

        # === Splitter Panels ===
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        self.control_panel = ControlPanel()
        self.control_panel.start_requested.connect(self.initiate_processing)
        self.control_panel.stop_requested.connect(self.stop_processing)

        self.output_panel = OutputPanel()

        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.output_panel)
        splitter.setSizes([267, 800])

    # ==================== Top Bar: About (Left) ====================
    def show_about(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "res", "icon.png")
        icon_url = QUrl.fromLocalFile(icon_path).toString()

        dlg = QDialog(self)
        dlg.setWindowTitle(self.t["about_title"])

        layout = QVBoxLayout(dlg)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        lbl_text = QLabel(self.t["about_text"].format(icon_url, config.APP_VERSION, config.APP_AUTHOR))
        lbl_text.setTextFormat(Qt.RichText)
        layout.addWidget(lbl_text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_gh = buttons.addButton(self.t["btn_about_git"], QDialogButtonBox.ActionRole)

        buttons.accepted.connect(dlg.accept)
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(config.PROJECT_URL)))

        layout.addWidget(buttons)

        dlg.exec()

    # ==================== Top Bar: Unload ====================
    def unload_model(self):
        # Trigger background worker to unload model from GPU memory.
        self.btn_unload.setEnabled(False)
        self.btn_unload.setText("...")

        self.unload_worker = ModelUnloadWorker(self.client)
        self.unload_worker.finished.connect(self.on_unload_finished)
        self.unload_worker.start()

    @Slot(bool, str)
    def on_unload_finished(self, success, message):
        self.btn_unload.setEnabled(True)
        self.btn_unload.setText(self.t["btn_unload"])

        if success:
            QMessageBox.information(self, self.t["title_info"], self.t[message])
        else:
            QMessageBox.critical(self, self.t["title_error"], message)

    # ==================== Top Bar: Language (Right) ====================
    def change_language(self, lang_name):
        self.current_lang_code = self.languages[lang_name]
        self.t = lang_handler.load_language(self.current_lang_code)
        self.apply_language()

    def apply_language(self):
        # Apply translation strings to all UI elements.
        # Top Bar
        self.btn_about.setText(self.t["btn_about"])
        self.btn_unload.setText(self.t["btn_unload"])

        self.lbl_prompt.setText(self.t["lbl_prompt"])

        # Reload prompts dropdown while preserving selection
        current_id = self.combo_prompts.currentData()
        self.combo_prompts.blockSignals(True) # Prevent change events during rebuild
        self.combo_prompts.clear()
        if "prompt_labels" in self.t:
            for pid, label in self.t["prompt_labels"].items():
                self.combo_prompts.addItem(label, pid)

        # Restore selection or use default
        if current_id:
            index = self.combo_prompts.findData(current_id)
            if index >= 0: self.combo_prompts.setCurrentIndex(index)
        else:
            index = self.combo_prompts.findData(config.DEFAULT_PROMPT)
            if index >= 0: self.combo_prompts.setCurrentIndex(index)

        self.combo_prompts.blockSignals(False)

        # Update child panels
        self.control_panel.update_language(self.t)
        self.output_panel.update_language(self.t)

    # ==================== Processing State ====================
    def set_processing_state(self, is_processing):
        # Toggle all UI elements between processing/idle states.
        self.control_panel.set_processing_state(is_processing)
        self.btn_unload.setEnabled(not is_processing)
        self.combo_lang.setEnabled(not is_processing)
        self.combo_prompts.setEnabled(not is_processing)

    # ==================== Processing Flow ====================
    @Slot(list)
    def initiate_processing(self, queue):
        # Called when control panel emits start_requested signal.
        pid = self.combo_prompts.currentData()
        prompt_template = config.PROMPTS.get(pid, config.PROMPTS[config.DEFAULT_PROMPT])
        model_name = config.OLLAMA_MODEL

        self.start_processing(queue, prompt_template, model_name, pid)

    def start_processing(self, queue, prompt_template, model_name, prompt_id=None):
        # Start OCR worker thread to process the queue.
        self.output_panel.clear()
        self.set_processing_state(True)
        self.batch_start_time = time.time()

        self.taskbar.set_progress(int(self.winId()), 0, len(queue))

        self.worker = OCRWorker(self.client, queue, prompt_template, model_name, prompt_id)

        # Connect worker signals -> UI updates
        self.worker.stream_chunk.connect(self.output_panel.append_text)
        self.worker.stream_chunk.connect(self.control_panel.on_stream_chunk)
        self.worker.box_detected.connect(self.control_panel.draw_box)
        self.worker.error_occurred.connect(lambda e: self.output_panel.append_text(f"\nERROR: {e}"))

        self.worker.image_started.connect(self.on_image_started)
        self.worker.image_finished.connect(self.on_image_finished)
        self.worker.finished_all.connect(self.on_finished)

        self.worker.start()

    def stop_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.output_panel.append_text(f"\n\n=== {self.t['msg_stopped']} ===")
            self.taskbar.stop_progress(int(self.winId()))

    # ==================== Processing Callbacks ====================
    @Slot(str, int)
    def on_image_started(self, display_name, index):
        self.output_panel.append_text(f"\n--- {self.t['msg_started'].format(display_name)} ---\n")
        self.control_panel.on_process_started(index)

    @Slot(str, float)
    def on_image_finished(self, display_name, duration):
        self.control_panel.increment_progress()
        self.output_panel.append_text(f"\n--- {self.t['msg_elapsed'].format(display_name, duration)} ---\n")

        # Update taskbar progress
        self.taskbar.set_progress(
            int(self.winId()), 
            self.control_panel.progress_bar.value(), 
            self.control_panel.progress_bar.maximum()
        )

    @Slot()
    def on_finished(self):
        # Called when all images have been processed.
        self.set_processing_state(False)
        self.control_panel.update_status()
        self.taskbar.stop_progress(int(self.winId()))

        self.output_panel.render_fancy_output()

        # Show completion dialog with total time
        if self.control_panel.progress_bar.value() == self.control_panel.progress_bar.maximum():
            total_duration = time.time() - self.batch_start_time
            total_str = self.t["msg_total"].format(total_duration)
            QMessageBox.information(self, self.t["title_done"], f"{self.t['msg_done']}\n{total_str}")