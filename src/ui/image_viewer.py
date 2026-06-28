# src/ui/image_viewer.py
# Widget that displays the current image with optional bounding boxes.

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QColor, QPen, QBrush, QPainter
from PySide6.QtCore import Qt, QRectF

class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setStyleSheet("background-color: transparent;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.pixmap_item = None
        self.current_image_size = (0, 0)
        self.target_size = (1024, 1024) # Model's expected input size

    def display_image(self, image_bytes):
        # Load and display an image from bytes data.
        self.scene.clear()
        self.pixmap_item = None
        self.current_image_size = (0, 0)

        qt_img = QImage()
        if not qt_img.loadFromData(image_bytes):
            return

        self.current_image_size = (qt_img.width(), qt_img.height())
        pixmap = QPixmap.fromImage(qt_img)
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))
        self.fit_content()

    def draw_box(self, coords, color=None, label=""):
        """
        Draw a bounding box overlay on the image.

        DeepSeek-OCR returns coordinates in a 0-999 normalized space.
        We convert these to actual pixel coordinates based on image size.

        See: https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.5-understanding-output#bounding-box-format
        coords: [x1, y1, x2, y2] in 0-999 scale
        color: QColor (optional, generates random if not provided)
        label: The element class string from grounding tags
        """
        if not self.pixmap_item or self.current_image_size == (0, 0):
            return

        img_w, img_h = self.current_image_size

        try:
            x1_norm, y1_norm, x2_norm, y2_norm = coords

            # Convert normalized coords (0-999) to pixel coords (0-img_size)
            real_x1 = (x1_norm / 999.0) * img_w
            real_y1 = (y1_norm / 999.0) * img_h
            real_x2 = (x2_norm / 999.0) * img_w
            real_y2 = (y2_norm / 999.0) * img_h

            w = real_x2 - real_x1
            h = real_y2 - real_y1

            rect_item = QGraphicsRectItem(QRectF(real_x1, real_y1, w, h))

            if color is None:
                # Generate random vibrant color
                # R < 200, G < 200, B < 255
                import random
                r = random.randint(0, 200)
                g = random.randint(0, 200)
                b = random.randint(0, 255)
                color = QColor(r, g, b)

            pen = QPen(color)

            # Adjust rendering style based on Label Type
            lbl = label.strip().lower()
            if lbl == 'title':
                pen.setWidth(4) # Thicker border for titles
            else:
                pen.setWidth(2) # Standard border for others

            rect_item.setPen(pen)

            # Semi-transparent fill using same color with alpha
            brush_color = QColor(color)
            brush_color.setAlpha(80) # ~30% opacity
            brush = QBrush(brush_color)
            rect_item.setBrush(brush)

            self.scene.addItem(rect_item)

        except Exception as e:
            print(f"Failed to draw box {coords}: {e}")

    def fit_content(self):
        # Scale view to fit entire scene content.
        if self.scene.sceneRect().width() > 0:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        # Re-fit content when widget is resized.
        super().resizeEvent(event)
        self.fit_content()
