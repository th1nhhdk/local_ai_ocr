# src/ui/output_panel.py
# Right panel that displays OCR results in both raw text and rendered markdown.

import os
import re
import html
import markdown
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton, QLabel, QTextEdit, QMenu
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import Qt, Slot, QUrl
from PySide6.QtGui import QTextCursor


# CSS styling for the fancy (rendered) output view
BROWSER_STYLE = """
<style>
body { background-color: #FFFFFF; color: #000000; font-family: "Times New Roman", serif; font-size: 13pt; line-height: 1.6; }
a { color: #0000EE; text-decoration: none; }
a:hover { text-decoration: underline; }
code { background-color: #F0F0F0; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; }
pre { background-color: #F0F0F0; padding: 10px; border-radius: 5px; overflow-x: auto; border: 1px solid #CCC; }
pre code { background-color: transparent; padding: 0; }
h1, h2, h3, h4, h5, h6 { color: #000000; margin-top: 1.5em; margin-bottom: 0.5em; }
h1 { border-bottom: 1px solid #CCCCCC; padding-bottom: 0.3em; }
blockquote { border-left: 4px solid #CCCCCC; margin-left: 0; padding-left: 15px; color: #666666; font-style: italic; }
ul, ol { padding-left: 25px; }
li { margin-bottom: 0.3em; }
table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
th, td { border: 1px solid #000000; padding: 8px; text-align: left; }
th { background-color: #F2F2F2; font-weight: bold; }
tr:nth-child(even) { background-color: #FAFAFA; }
</style>
"""


def balance_latex_delimiters(latex):
    """
    Fix unbalanced \\left and \\right delimiters in LaTeX.
    LaTeX requires matching \\left and \\right pairs. DeepSeek-OCR sometime
    outputs unbalanced delimiters, which cause MathJax to fail when rendering.
    This function:
    1. Removes orphan \\right commands (no matching \\left)
    2. Adds \\right. (invisible delimiter) for unmatched \\left
    """
    # Find all \left and \right commands with their positions
    commands = []
    for m in re.finditer(r'(\\left|\\right)', latex):
        commands.append((m.start(), m.end(), m.group(0)))

    to_remove = set()
    stack = 0

    # Track depth: \left increases, \right decreases
    for start, end, cmd in commands:
        if cmd == r'\left':
            stack += 1
        else:
            if stack > 0:
                stack -= 1
            else:
                # Unmatched \right - mark for removal
                to_remove.add(start)

    # Rebuild string, skipping marked positions
    fixed_latex = ""
    last_idx = 0
    for start, end, cmd in commands:
        if start in to_remove:
            fixed_latex += latex[last_idx:start]
            last_idx = end

    fixed_latex += latex[last_idx:]

    # Add invisible delimiters for unmatched \left
    if stack > 0:
        fixed_latex += (r" \right." * stack)

    return fixed_latex


# ==================== Tab 2: Fancy Output ====================
class FancyOutput(QWebEngineView):
    # WebView that renders markdown with MathJax LaTeX support.
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page().setBackgroundColor(Qt.white)

    def set_markdown(self, md_content):
        # Convert markdown to HTML and render with MathJax.
        if not md_content:
            self.setHtml("")
            return

        try:
            # 1. Extract and protect LaTeX blocks from markdown processing
            # Markdown would destroy LaTeX syntax, so we replace with placeholders
            math_blocks = []

            def replace_math(match):
                block = match.group(0)
                block = balance_latex_delimiters(block)
                math_blocks.append(block)
                return f"MATHJAXBLOCKPLACEHOLDER{len(math_blocks)-1}END"

            # Match both display (\[...\]) and inline (\(...\)) math
            pattern = re.compile(r'(\\\[.*?\\\])|(\\\(.*?\\\))', re.DOTALL)
            processed_md = pattern.sub(replace_math, md_content)

            # 2. Convert markdown to HTML
            html_content = markdown.markdown(processed_md, extensions=['tables', 'fenced_code', 'nl2br'])

            # 3. Restore LaTeX blocks, escaped for HTML safety
            for i, block in enumerate(math_blocks):
                safe_block = html.escape(block)
                html_content = html_content.replace(f"MATHJAXBLOCKPLACEHOLDER{i}END", safe_block)

            # 4. Setup MathJax
            base_path = os.path.dirname(os.path.abspath(__file__))
            project_path = os.path.dirname(base_path)
            mathjax_path = os.path.join(project_path, "res", "mathjax.js")
            mathjax_url = QUrl.fromLocalFile(mathjax_path).toString()

            mathjax_script = f"""
            <script>
            MathJax = {{
              tex: {{
                inlineMath: [['\\\\(', '\\\\)']],
                displayMath: [['\\\\[', '\\\\]']],
                processEscapes: true
              }},
              options: {{
                ignoreHtmlClass: 'tex2jax_ignore',
                processHtmlClass: 'tex2jax_process'
              }}
            }};
            </script>
            <script id="MathJax-script" async src="{mathjax_url}"></script>
            """

            full_html = f"<html><head>{BROWSER_STYLE}{mathjax_script}</head><body>{html_content}</body></html>"
            self.setHtml(full_html, QUrl.fromLocalFile(project_path))
        except Exception as e:
            print(f"Markdown render error: {e}")

    def copy_content(self):
        self.setFocus()
        page = self.page()
        page.triggerAction(QWebEnginePage.WebAction.SelectAll)
        page.triggerAction(QWebEnginePage.WebAction.Copy)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(self.page().action(QWebEnginePage.WebAction.Copy))
        menu.addAction(self.page().action(QWebEnginePage.WebAction.SelectAll))
        menu.exec(event.globalPos())


# ==================== Main Widget ====================
class OutputPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.t = {}  # Translation dictionary

        # === Tabs ===
        self.tabs = QTabWidget()

        # Tab 1: Raw Output
        self.tab_raw = QWidget()
        raw_layout = QVBoxLayout(self.tab_raw)
        raw_layout.setContentsMargins(0, 0, 0, 0)
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        raw_layout.addWidget(self.text_output)

        # Tab 2: Fancy Output
        self.web_view = FancyOutput()

        self.tabs.addTab(self.tab_raw, "")
        self.tabs.addTab(self.web_view, "")
        self.tabs.setTabEnabled(1, False)  # Disabled until processing completes
        self.tabs.currentChanged.connect(self._update_copy_button_text)

        # === Bottom Controls ===
        self.lbl_proofread = QLabel()
        self.lbl_proofread.setObjectName("lbl_proofread")
        self.lbl_proofread.setAlignment(Qt.AlignCenter)

        self.btn_copy = QPushButton()
        self.btn_copy.clicked.connect(self.copy_output)

        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.lbl_proofread)
        self.layout.addWidget(self.btn_copy)

    # ==================== Language ====================
    def update_language(self, t):
        self.t = t
        self.lbl_proofread.setText(t["lbl_proofread"])
        self.tabs.setTabText(0, t["tab_raw"])
        self.tabs.setTabText(1, t["tab_fancy"])
        self._update_copy_button_text()

    def _update_copy_button_text(self):
        if not self.t or "btn_copy" not in self.t:
            return
        current_tab_text = self.tabs.tabText(self.tabs.currentIndex())
        self.btn_copy.setText(self.t["btn_copy"].format(current_tab_text))

    # ==================== Tab 1: Raw Output ====================
    @Slot(str)
    def append_text(self, text):
        # Append streaming text to raw output. Switches to raw tab if on fancy.
        if self.tabs.currentIndex() != 0:
             self.tabs.setCurrentIndex(0)

        if self.tabs.isTabEnabled(1):
            self.tabs.setTabEnabled(1, False)

        # Move cursor to end, insert text, keep cursor at end (auto-scroll)
        self.text_output.moveCursor(QTextCursor.End)
        self.text_output.insertPlainText(text)
        self.text_output.moveCursor(QTextCursor.End)

    # ==================== Tab 2: Fancy Output ====================
    def render_fancy_output(self):
        # Convert raw text to rendered markdown.
        raw_md = self.text_output.toPlainText()
        if not raw_md.strip():
            return

        self.web_view.set_markdown(raw_md)
        self.tabs.setTabEnabled(1, True)
        self.tabs.setCurrentIndex(1)

    # ==================== Utility ====================
    def clear(self):
        self.text_output.clear()
        self.web_view.set_markdown("")
        self.tabs.setTabEnabled(1, False)
        self.tabs.setCurrentIndex(0)

    def copy_output(self):
        if self.tabs.currentIndex() == 0:
            self.text_output.selectAll()
            self.text_output.copy()
        else:
            self.web_view.copy_content()
