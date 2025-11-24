# src/gui.py
import time
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QListWidget, QFileDialog,
                               QLabel, QProgressBar, QSplitter, QComboBox,
                               QMessageBox, QGroupBox, QDialog, QDialogButtonBox, QFormLayout, QSpinBox)
from PySide6.QtCore import Qt, Slot, QUrl, QThread, Signal
from PySide6.QtGui import QTextCursor, QDesktopServices, QIcon

import constants
import file_handler
import lang_handler
from worker import OCRWorker

class PageRangeDialog(QDialog):
    def __init__(self, filename, total_pages, translations, parent=None):
        super().__init__(parent)
        self.t = translations
        self.setWindowTitle(self.t["dlg_page_range_title"])
        self.setFixedWidth(350)

        layout = QVBoxLayout(self)

        # Info Label
        info_label = QLabel(self.t["dlg_page_range_msg"].format(filename, total_pages))
        layout.addWidget(info_label)

        # Form for Range
        form = QFormLayout()

        self.spin_start = QSpinBox()
        self.spin_start.setRange(1, total_pages)
        self.spin_start.setValue(1)

        self.spin_end = QSpinBox()
        self.spin_end.setRange(1, total_pages)
        self.spin_end.setValue(total_pages)

        form.addRow(self.t["dlg_page_range_start"], self.spin_start)
        form.addRow(self.t["dlg_page_range_end"], self.spin_end)
        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        # Only check logic when user is done
        if self.spin_start.value() > self.spin_end.value():
            QMessageBox.critical(self, self.t["msg_error"], self.t["dlg_page_range_error"])
            return
        self.accept()

    def get_range(self):
        return self.spin_start.value(), self.spin_end.value()

class UnloadWorker(QThread):
    finished = Signal(bool, str) # success, message_key_or_error

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        try:
            is_loaded = True
            try:
                response = self.client.ps()
                if hasattr(response, 'models'):
                    models = response.models
                else:
                    models = response.get('models', [])

                is_loaded = False
                for m in models:
                    name = m.model if hasattr(m, 'model') else m.get('model')
                    if name == constants.DEFAULT_MODEL:
                        is_loaded = True
                        break
            except:
                # If ps() fails, assume loaded to force an unload attempt
                is_loaded = True

            if is_loaded:
                self.client.chat(model=constants.DEFAULT_MODEL, messages=[], keep_alive=0)
                self.finished.emit(True, "msg_model_unloaded")
            else:
                self.finished.emit(True, "msg_model_not_loaded")
        except Exception as e:
            self.finished.emit(False, str(e))

class OCRWindow(QMainWindow):
    def __init__(self, ollama_client):
        super().__init__()
        self.client = ollama_client

        self.setWindowTitle(f"Local AI OCR ({constants.APP_VERSION})")
        self.resize(1067, 600) # Six-seven... Six-seven... Six-seven...

        # Set Window Icon (Specific to this window instance)
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.current_lang = lang_handler.get_default_language()
        self.t = constants.TRANSLATIONS[self.current_lang]

        self.image_queue = [] 
        self.worker = None
        self.unload_worker = None
        self.batch_start_time = 0.0

        self.init_ui()

        self.apply_language() 

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Top Bar
        top_bar = QHBoxLayout()

        # About button
        self.btn_about = QPushButton()
        self.btn_about.clicked.connect(self.show_about)
        top_bar.addWidget(self.btn_about)

        # Unload button
        self.btn_unload = QPushButton()
        self.btn_unload.clicked.connect(self.unload_model)
        top_bar.addWidget(self.btn_unload)

        top_bar.addStretch()

        top_bar.addWidget(QLabel("Language / Ngôn ngữ:"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(constants.TRANSLATIONS.keys())
        self.combo_lang.setCurrentText(self.current_lang)
        self.combo_lang.currentTextChanged.connect(self.change_language)
        top_bar.addWidget(self.combo_lang)
        main_layout.addLayout(top_bar)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # --- Left Panel ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add_img = QPushButton()
        self.btn_add_pdf = QPushButton()
        self.btn_clear = QPushButton()

        self.btn_add_img.clicked.connect(self.add_images)
        self.btn_add_pdf.clicked.connect(self.add_pdf)
        self.btn_clear.clicked.connect(self.clear_queue)

        btn_layout.addWidget(self.btn_add_img)
        btn_layout.addWidget(self.btn_add_pdf)
        btn_layout.addWidget(self.btn_clear)
        left_layout.addLayout(btn_layout)

        # List
        self.lbl_queue = QLabel()
        self.list_widget = QListWidget()
        left_layout.addWidget(self.lbl_queue)
        left_layout.addWidget(self.list_widget)

        # Prompts
        self.group_settings = QGroupBox()
        p_layout = QVBoxLayout()
        self.lbl_prompt = QLabel()
        self.combo_prompts = QComboBox()
        self.combo_prompts.currentIndexChanged.connect(self.on_prompt_change)

        p_layout.addWidget(self.lbl_prompt)
        p_layout.addWidget(self.combo_prompts)
        self.group_settings.setLayout(p_layout)
        left_layout.addWidget(self.group_settings)

        # Run/Stop
        run_layout = QHBoxLayout()

        self.btn_run = QPushButton()
        self.btn_run.setFixedHeight(40)
        self.btn_run.setObjectName("btnRun")
        self.btn_run.clicked.connect(self.start_processing)

        self.btn_stop = QPushButton()
        self.btn_stop.setFixedHeight(40)
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.clicked.connect(self.stop_processing)
        self.btn_stop.setEnabled(False) 

        run_layout.addWidget(self.btn_run)
        run_layout.addWidget(self.btn_stop)
        left_layout.addLayout(run_layout)

        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)
        splitter.addWidget(left_panel)

        # --- Right Panel ---
        right_panel = QWidget()
        r_layout = QVBoxLayout(right_panel)
        self.lbl_output = QLabel()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.btn_copy = QPushButton()
        self.btn_copy.clicked.connect(self.text_output.selectAll)
        self.btn_copy.clicked.connect(self.text_output.copy)

        r_layout.addWidget(self.lbl_output)
        r_layout.addWidget(self.text_output)

        self.lbl_proofread = QLabel()
        self.lbl_proofread.setObjectName("lblProofread")
        self.lbl_proofread.setAlignment(Qt.AlignCenter)
        r_layout.addWidget(self.lbl_proofread)

        r_layout.addWidget(self.btn_copy)
        splitter.addWidget(right_panel)
        splitter.setSizes([267, 800])

    def change_language(self, lang_name):
        self.current_lang = lang_name
        self.t = constants.TRANSLATIONS[lang_name]
        self.apply_language()

    def apply_language(self):
        self.btn_about.setText(self.t["btn_about"])
        self.btn_unload.setText(self.t["btn_unload"])

        self.btn_add_img.setText(self.t["btn_add_img"])
        self.btn_add_pdf.setText(self.t["btn_add_pdf"])
        self.btn_clear.setText(self.t["btn_clear"])
        self.btn_stop.setText(self.t["btn_stop"]) 
        self.lbl_queue.setText(self.t["lbl_queue"])
        self.group_settings.setTitle(self.t["group_settings"])
        self.lbl_prompt.setText(self.t["lbl_prompt"])
        self.lbl_output.setText(self.t["lbl_output"])
        self.lbl_proofread.setText(self.t["lbl_proofread"])

        self.btn_copy.setText(self.t["btn_copy"])

        current_id = self.combo_prompts.currentData()
        self.combo_prompts.blockSignals(True) 
        self.combo_prompts.clear()

        prompt_labels = self.t["prompt_labels"]
        for pid, label in prompt_labels.items():
            self.combo_prompts.addItem(label, pid)

        if current_id:
            index = self.combo_prompts.findData(current_id)
            if index >= 0:
                self.combo_prompts.setCurrentIndex(index)
        else:
            index = self.combo_prompts.findData("p_ocr")
            if index >= 0:
                self.combo_prompts.setCurrentIndex(index)

        self.combo_prompts.blockSignals(False)
        self.update_status()

    def show_about(self):
        # Resolve absolute path for the HTML img tag
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        icon_url = QUrl.fromLocalFile(icon_path).toString()

        msg = QMessageBox(self)
        msg.setWindowTitle(self.t["about_title"])
        msg.setText(self.t["about_text"].format(icon_url, constants.APP_VERSION, constants.APP_AUTHOR))
        btn_gh = msg.addButton(self.t["btn_about_github"], QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Ok)
        msg.exec()

        if msg.clickedButton() == btn_gh:
            QDesktopServices.openUrl(QUrl(constants.PROJECT_URL))

    def on_prompt_change(self):
        # Warning the user if they pick Document to Markdown mode
        pid = self.combo_prompts.currentData()
        if pid == "p_markdown":
            QMessageBox.warning(self, "Warning", self.t["msg_markdown_warn"])

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, self.t["btn_add_img"], "", "Images (*.png *.jpg *.webp)")
        for f in files:
            name = os.path.basename(f)
            self.image_queue.append((name, f, -1)) 
            self.list_widget.addItem(name)
        self.update_status()

    def add_pdf(self):
        files, _ = QFileDialog.getOpenFileNames(self, self.t["btn_add_pdf"], "", "PDF Files (*.pdf)")
        for f in files:
            try:
                count = file_handler.get_pdf_page_count(f)
                base_name = os.path.basename(f)
                start_p = 1
                end_p = count

                # Range Dialog
                if count >= 2:
                    dlg = PageRangeDialog(base_name, count, self.t, self)
                    if dlg.exec() == QDialog.Accepted:
                        start_p, end_p = dlg.get_range()
                    else:
                        continue 

                for i in range(start_p - 1, end_p):
                    name = f"{base_name} - P{i+1}"
                    self.image_queue.append((name, f, i)) 
                    self.list_widget.addItem(name)
            except Exception as e:
                QMessageBox.critical(self, self.t["msg_error"], str(e))
        self.update_status()

    def clear_queue(self):
        self.image_queue.clear()
        self.list_widget.clear()
        self.update_status()

    def update_status(self):
        count = len(self.image_queue)
        self.btn_run.setText(self.t["status_ready"].format(count))
        if not self.worker or not self.worker.isRunning():
            self.btn_run.setEnabled(count > 0)

    @Slot(str)
    def safe_append(self, text):
        self.text_output.moveCursor(QTextCursor.End)
        self.text_output.insertPlainText(text)
        self.text_output.moveCursor(QTextCursor.End)

    def start_processing(self):
        if not self.image_queue: return

        # Disclaimer about infinite loop 
        QMessageBox.information(self, "Disclaimer", self.t["msg_loop_disclaimer"])

        pid = self.combo_prompts.currentData() 
        prompt_template = constants.PROMPTS[pid] 

        # Get model from constants.py
        model_name = constants.DEFAULT_MODEL

        # Prepare UI for processing
        self.set_processing_state(True)
        self.text_output.clear()
        self.progress_bar.setMaximum(len(self.image_queue))
        self.progress_bar.setValue(0)
        self.batch_start_time = time.time()

        # Start the worker thread
        self.worker = OCRWorker(self.client, self.image_queue, prompt_template, model_name)
        self.worker.stream_chunk.connect(self.safe_append)
        self.worker.image_started.connect(self.safe_append)
        self.worker.error_occurred.connect(lambda e: self.safe_append(f"\nERROR: {e}"))
        self.worker.image_finished.connect(self.on_image_finished)
        self.worker.finished_all.connect(self.on_finished)
        self.worker.start()

    def stop_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.safe_append(f"\n\n>>> {self.t['status_stopped']} <<<\n")

    def set_processing_state(self, is_processing):
        # Enabling/disabling buttons based on program state
        self.btn_run.setEnabled(not is_processing)
        self.btn_stop.setEnabled(is_processing)
        inputs_enabled = not is_processing
        self.btn_add_img.setEnabled(inputs_enabled)
        self.btn_add_pdf.setEnabled(inputs_enabled)
        self.btn_clear.setEnabled(inputs_enabled)
        self.combo_lang.setEnabled(inputs_enabled)
        self.combo_prompts.setEnabled(inputs_enabled)
        self.btn_unload.setEnabled(inputs_enabled)

    @Slot(float)
    def on_image_finished(self, duration):
        # Update progress bar
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        time_str = self.t["msg_elapsed"].format(duration)
        self.safe_append(f"\n--- {time_str} ---\n\n") 

    @Slot()
    def on_finished(self):
        self.set_processing_state(False)
        self.update_status() 

        if self.progress_bar.value() == self.progress_bar.maximum():
            total_duration = time.time() - self.batch_start_time
            total_str = self.t["msg_total"].format(total_duration)
            QMessageBox.information(self, "Done", f"{self.t['msg_done']}\n{total_str}")

    def unload_model(self):
        # Disable button to prevent multiple clicks
        self.btn_unload.setEnabled(False)
        self.btn_unload.setText("...")

        self.unload_worker = UnloadWorker(self.client)
        self.unload_worker.finished.connect(self.on_unload_finished)
        self.unload_worker.start()

    @Slot(bool, str)
    def on_unload_finished(self, success, message):
        self.btn_unload.setEnabled(True)
        self.btn_unload.setText(self.t["btn_unload"])

        if success:
            QMessageBox.information(self, "Info", self.t[message])
        else:
            QMessageBox.critical(self, self.t["msg_error"], message)