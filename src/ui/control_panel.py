# src/ui/control_panel.py
# Left panel containing file queue controls, image viewer, and processing buttons.

import os
import random
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QListWidget, QFileDialog, QLabel,
                               QProgressBar, QMessageBox, QDialog, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QColor

import config
import file_handler
from .dialogs import PageRangeDialog
from .image_viewer import ImageViewer
from .image_loader import ImageLoaderThread


class ControlPanel(QWidget):
    # Signals to communicate with MainWindow
    start_requested = Signal(list) # Emitted when Run button clicked
    stop_requested = Signal() # Emitted when Stop button clicked

    # ==================== Initialization ====================
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Queue: list of (display_name, filepath, page_index) tuples
        # page_index = -1 for images, 0+ for PDF pages
        self.image_queue = []

        # Stores bounding boxes per image: {index: [(coords, color), ...]}
        self.image_boxes = {}
        self.current_processing_index = -1
        self.t = {} # Translation dictionary

        self.loader_thread = None # Background thread for loading images

        # Debounce timer to prevent RAM spikes when scrolling fast
        # Without this scrolling too fast = 100% RAM usage
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(200) # Wait 200ms after selection settles
        self.debounce_timer.timeout.connect(self._perform_load_image)

        # === Top Row: Add/Clear Buttons ===
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
        self.layout.addLayout(btn_layout)

        # === Queue List ===
        self.lbl_queue = QLabel()
        self.list_widget = QListWidget()
        self.layout.addWidget(self.lbl_queue)
        self.layout.addWidget(self.list_widget)

        # === Run/Stop Buttons ===
        run_layout = QHBoxLayout()
        self.btn_run = QPushButton()
        self.btn_run.setObjectName("btn_run")
        self.btn_run.setFixedHeight(40)
        self.btn_run.clicked.connect(self.on_start_click)

        self.btn_stop = QPushButton()
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setFixedHeight(40)
        self.btn_stop.clicked.connect(self.on_stop_click)

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(False)

        run_layout.addWidget(self.btn_run)
        run_layout.addWidget(self.btn_stop)
        self.layout.addLayout(run_layout)

        # === Image Viewer & Navigation Buttons ===
        # Wrap viewer and buttons in a horizontal layout
        viewer_layout = QHBoxLayout()
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        viewer_layout.setSpacing(2)

        self.image_viewer = ImageViewer()
        self.image_viewer.setMinimumHeight(250)
        self.image_viewer.setMinimumWidth(100)
        viewer_layout.addWidget(self.image_viewer)

        # Right side: Up/Down Arrow Buttons
        arrow_layout = QVBoxLayout()
        arrow_layout.setContentsMargins(0, 0, 0, 0)
        arrow_layout.setSpacing(0)

        self.btn_up = QPushButton("▲")
        self.btn_up.setObjectName("btn_up")
        self.btn_up.setFixedWidth(45)
        self.btn_up.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.btn_up.clicked.connect(self.move_selection_up)

        self.btn_down = QPushButton("▼")
        self.btn_down.setObjectName("btn_down")
        self.btn_down.setFixedWidth(45)
        self.btn_down.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.btn_down.clicked.connect(self.move_selection_down)

        arrow_layout.addWidget(self.btn_up)
        arrow_layout.addWidget(self.btn_down)

        viewer_layout.addLayout(arrow_layout)

        self.layout.addLayout(viewer_layout)


        # === Progress Bar ===
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.list_widget.currentItemChanged.connect(self.on_queue_item_changed)

    # ==================== State Management ====================
    def update_language(self, t):
        self.t = t
        self.btn_add_img.setText(t["btn_add_img"])
        self.btn_add_pdf.setText(t["btn_add_pdf"])
        self.btn_clear.setText(t["btn_clear"])
        self.btn_stop.setText(t["btn_stop"])
        self.lbl_queue.setText(t["lbl_queue"])
        self.update_status()

    def update_status(self):
        count = len(self.image_queue)
        if "btn_run_ready" in self.t:
            self.btn_run.setText(self.t["btn_run_ready"].format(count))

        # Only enable Run if not currently processing
        if not self.btn_stop.isEnabled():
             self.btn_run.setEnabled(count > 0)

        # Navigation buttons enabled only if we have more than 1 item
        can_navigate = count > 1
        self.btn_up.setEnabled(can_navigate)
        self.btn_down.setEnabled(can_navigate)

    def set_processing_state(self, is_processing):
        # Toggle UI elements between processing/idle states.
        self.btn_run.setEnabled(not is_processing)
        self.btn_stop.setEnabled(is_processing)

        # Disable inputs during processing to prevent queue modification
        inputs_enabled = not is_processing
        self.btn_add_img.setEnabled(inputs_enabled)
        self.btn_add_pdf.setEnabled(inputs_enabled)
        self.btn_clear.setEnabled(inputs_enabled)

    # ==================== Top Row: Add Images (Left) ====================
    def add_images(self):
        # Build filter from config
        ext_filter = "Images (" + " ".join(f"*{ext}" for ext in config.IMAGE_EXTENSIONS) + ")"
        files, _ = QFileDialog.getOpenFileNames(self, self.t["btn_add_img"], "", ext_filter)
        self.add_image_files(files)

    def add_image_files(self, filepaths):
        # Add image files to queue programmatically (used by dialog and drag/drop).
        for f in filepaths:
            name = os.path.basename(f)
            self.image_queue.append((name, f, -1))  # -1 = not a PDF page
            self.list_widget.addItem(name)

        # Auto-select first item if nothing selected
        if self.list_widget.currentRow() == -1 and self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

        self.update_status()

    # ==================== Top Row: Add PDF (Middle) ====================
    def add_pdf(self):
        files, _ = QFileDialog.getOpenFileNames(self, self.t["btn_add_pdf"], "", "PDF Files (*.pdf)")
        self.add_pdf_files(files)

    def add_pdf_files(self, filepaths):
        # Add PDF files to queue programmatically (used by dialog and drag/drop).
        for f in filepaths:
            try:
                count = file_handler.get_pdf_page_count(f)
                base_name = os.path.basename(f)
                start_p, end_p = 1, count

                # Show page range dialog for multi-page PDFs
                if count >= 2:
                    dlg = PageRangeDialog(base_name, count, self.t, self)
                    if dlg.exec() == QDialog.Accepted:
                        start_p, end_p = dlg.get_range()
                    else:
                        continue  # User cancelled

                # Add each selected page to queue
                for i in range(start_p - 1, end_p):
                    name = f"{base_name} :P{i+1}"
                    self.image_queue.append((name, f, i))  # i = 0-based page index
                    self.list_widget.addItem(name)
            except Exception as e:
                QMessageBox.critical(self, self.t["title_error"], str(e))

        if self.list_widget.currentRow() == -1 and self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

        self.update_status()

    # ==================== List Navigation ====================
    def move_selection_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            self.list_widget.setCurrentRow(row - 1)

    def move_selection_down(self):
        row = self.list_widget.currentRow()
        if row < self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(row + 1)

    # ==================== Top Row: Clear (Right) ====================
    def clear_queue(self):
        self.image_queue.clear()
        self.image_boxes.clear()
        self.list_widget.clear()
        self.image_viewer.scene.clear()
        self.update_status()

    # ==================== Queue List ====================
    def on_queue_item_changed(self, current, previous):
        # Handle queue selection change - load image in background thread.
        if not current:
            return

        row = self.list_widget.row(current)
        if row < 0 or row >= len(self.image_queue):
            return

        name, path, page_index = self.image_queue[row]

        # Cancel any pending load operation
        if self.loader_thread is not None and self.loader_thread.isRunning():
            self.loader_thread.cancel()
            self.loader_thread = None

        # Cancel pending debounce
        self.debounce_timer.stop()

        # Check if we should load immediately or debounce
        # If the user is just clicking once, we want it somewhat snappy,
        # but if they are scrolling, we want to wait.
        # For simplicity, always debounce slightly or just restart the timer.
        self.debounce_timer.start()

    def _perform_load_image(self):
        # Called by timer to actually start loading
        current = self.list_widget.currentItem()
        if not current: return

        row = self.list_widget.row(current)
        if row < 0 or row >= len(self.image_queue): return

        name, path, page_index = self.image_queue[row]

        if self.loader_thread is not None and self.loader_thread.isRunning():
             self.loader_thread.cancel()

        self.loader_thread = ImageLoaderThread(path, page_index)
        self.loader_thread.image_loaded.connect(lambda b: self.on_image_loaded(b, row))
        self.loader_thread.error_occurred.connect(lambda e: print(f"Error loading image: {e}"))
        self.loader_thread.start()

    def on_image_loaded(self, img_bytes, row):
        # Callback when background image load completes.
        # Ignore if user already switched to different item
        if self.list_widget.currentRow() != row:
            return

        try:
            self.image_viewer.display_image(img_bytes)

            # Restore any previously drawn bounding boxes for this image
            if row in self.image_boxes:
                for coords, color in self.image_boxes[row]:
                    self.image_viewer.draw_box(coords, color)
        except Exception as e:
            print(f"Error displaying loaded image: {e}")

    # ==================== Run Button (Left) ====================
    def on_start_click(self):
        if not self.image_queue: return

        QMessageBox.information(self, self.t["title_disclaimer"], self.t["msg_loop_disclaimer"])

        self.progress_bar.setMaximum(len(self.image_queue))
        self.progress_bar.setValue(0)

        self.start_requested.emit(self.image_queue)

    # ==================== Stop Button (Right) ====================
    def on_stop_click(self):
        self.stop_requested.emit()

    # ==================== Processing Callbacks ====================
    def on_process_started(self, index):
        # Called when worker starts processing an image.
        # Clear boxes on first image (new batch)
        if index == 0:
            self.image_boxes.clear()
            current_row = self.list_widget.currentRow()
            if current_row >= 0 and current_row < len(self.image_queue):
                _, path, page_index = self.image_queue[current_row]
                if self.loader_thread is not None and self.loader_thread.isRunning():
                    self.loader_thread.cancel()
                self.loader_thread = ImageLoaderThread(path, page_index)
                self.loader_thread.image_loaded.connect(lambda b: self.on_image_loaded(b, current_row))
                self.loader_thread.start()

        self.current_processing_index = index
        # Auto-scroll queue to currently processing item
        if 0 <= index < self.list_widget.count():
            self.list_widget.setCurrentRow(index)

    def on_stream_chunk(self, text):
        pass # Output is handled by OutputPanel

    def draw_box(self, coords):
        # Draw bounding box for current image and store for persistence.
        if self.current_processing_index == -1: return

        # Generate random vibrant color
        # R < 200, G < 200, B < 255
        r = random.randint(0, 200)
        g = random.randint(0, 200)
        b = random.randint(0, 255)
        color = QColor(r, g, b)

        # Store for redrawing when switching images
        if self.current_processing_index not in self.image_boxes:
            self.image_boxes[self.current_processing_index] = []
        self.image_boxes[self.current_processing_index].append((coords, color))

        # Draw immediately if this image is currently visible
        if self.list_widget.currentRow() == self.current_processing_index:
            self.image_viewer.draw_box(coords, color)

    # ==================== Progress Bar ====================
    def increment_progress(self):
        # Increment progress bar and return True if all items complete.
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        return self.progress_bar.value() == self.progress_bar.maximum()
