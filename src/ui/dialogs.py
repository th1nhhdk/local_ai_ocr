# src/ui/dialogs.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout, QSpinBox, QDialogButtonBox, QMessageBox


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
            QMessageBox.critical(self, self.t["title_error"], self.t["dlg_page_range_error"])
            return
        self.accept()

    def get_range(self):
        return self.spin_start.value(), self.spin_end.value()