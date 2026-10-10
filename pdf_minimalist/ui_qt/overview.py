"""Navigator minimap: baseline page thumbnail + viewport rect. Click to center."""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QImage, QPainter, QPen, QColor


class OverviewMap(QWidget):
    """Small preview mirroring the current view on the original (baseline) page.

    Shows the whole baseline page with a rectangle for the main view's visible
    region. Click/drag recenters the main view there.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.setToolTip("Navigator — shows where the main view is on the original; click to jump")
        self._img: QImage | None = None
        self._rect = QRectF()  # viewport rect, in image coords
        self.navigate = None  # callback(QPointF image coords) -> main view centers there

    def set_page(self, qimg: QImage | None):
        self._img = qimg.copy() if qimg is not None else None
        self._rect = QRectF()
        self.update()

    def set_view(self, visible_scene: QRectF, origin: QPointF):
        """visible_scene: main view's visible rect in scene coords; origin: page offset."""
        if self._img is None:
            return
        self._rect = QRectF(visible_scene.translated(-origin.x(), -origin.y()))
        self.update()

    def _geom(self):
        if self._img is None or self._img.isNull():
            return None, None
        iw, ih = self._img.width(), self._img.height()
        s = min(self.width() / iw, self.height() / ih)
        w, h = iw * s, ih * s
        ox, oy = (self.width() - w) / 2, (self.height() - h) / 2
        return s, (ox, oy, w, h)

    def paintEvent(self, e):
        super().paintEvent(e)
        g = self._geom()
        if g[0] is None:
            return
        s, (ox, oy, w, h) = g
        p = QPainter(self)
        p.drawImage(int(ox), int(oy), self._img.scaled(int(w), int(h),
                                                       Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if not self._rect.isNull():
            p.setPen(QPen(QColor(200, 30, 30), 2))
            p.drawRect(int(ox + self._rect.x() * s), int(oy + self._rect.y() * s),
                       int(self._rect.width() * s), int(self._rect.height() * s))
        p.end()

    def _to_image(self, pos) -> QPointF | None:
        g = self._geom()
        if g[0] is None:
            return None
        s, (ox, oy, w, h) = g
        return QPointF((pos.x() - ox) / s, (pos.y() - oy) / s)

    def mousePressEvent(self, e):
        pt = self._to_image(e.position())
        if pt is not None and self.navigate is not None:
            self.navigate(pt)
        e.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            pt = self._to_image(e.position())
            if pt is not None and self.navigate is not None:
                self.navigate(pt)
            e.accept()
        else:
            super().mouseMoveEvent(e)
