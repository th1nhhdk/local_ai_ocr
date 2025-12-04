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
        self.fit_content()

    def draw_box(self, coords, color=None):
        """
        Draw a bounding box overlay on the image.

        DeepSeek-OCR returns coordinates in a 0-1000 normalized space.
        We convert these to actual pixel coordinates based on image size.

        coords: [x1, y1, x2, y2] in 0-1000 scale
        color: QColor (optional, generates random if not provided)
        """
        if not self.pixmap_item or self.current_image_size == (0, 0):
            return

        img_w, img_h = self.current_image_size

        try:
            x1_norm, y1_norm, x2_norm, y2_norm = coords

            # Convert normalized coords (0-1000) to pixel coords (0-img_size)
            real_x1 = (x1_norm / 1000.0) * img_w
            real_y1 = (y1_norm / 1000.0) * img_h
            real_x2 = (x2_norm / 1000.0) * img_w
            real_y2 = (y2_norm / 1000.0) * img_h

            w = real_x2 - real_x1
            h = real_y2 - real_y1

            rect_item = QGraphicsRectItem(QRectF(real_x1, real_y1, w, h))

            if color is None:
                # Generate random vibrant color using HSL color space
                # Hue: random angle, Saturation: max (255), Lightness: middle (127)
                import random
                hue = random.randint(0, 359)
                color = QColor.fromHsl(hue, 255, 127)

            pen = QPen(color)
            pen.setWidth(4) # Thick border for visibility
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
        if self.scene.itemsBoundingRect().width() > 0:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        # Re-fit content when widget is resized.
        super().resizeEvent(event)
        self.fit_content()
