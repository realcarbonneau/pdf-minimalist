"""Smooth pan/zoom page viewer: wheel=scroll, ctrl+wheel=zoom to cursor, drag=pan.

Designer ruling: all panes stay synced — zoom/pan in either pane mirrors to
its peers (used for the original/preview pair).
"""
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QPoint, QPointF
from PySide6.QtGui import QPixmap, QImage, QPainter, QTransform


class PdfGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._item = QGraphicsPixmapItem()
        self._scene.addItem(self._item)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self._zoom = 1.0
        self._peers: list["PdfGraphicsView"] = []
        self._syncing = False
        self.horizontalScrollBar().valueChanged.connect(lambda _v: self._push())
        self.verticalScrollBar().valueChanged.connect(lambda _v: self._push())

    def link(self, other: "PdfGraphicsView"):
        """Mirror all zoom/pan to `other` (call both ways for a pair)."""
        if other is not self and other not in self._peers:
            self._peers.append(other)

    def set_image(self, qimg: QImage):
        self._scene.clear()
        self._item = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
        self._scene.addItem(self._item)
        self._zoom = 1.0
        self.resetTransform()
        self.fitInView(self._item, Qt.KeepAspectRatio)
        self._push()

    def wheelEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            factor = 1.25 if e.angleDelta().y() > 0 else 1 / 1.25
            new = self._zoom * factor
            if 0.1 <= new <= 20:
                self._zoom = new
                self.scale(factor, factor)
            e.accept()
            self._push()
        else:
            super().wheelEvent(e)  # page scroll; scrollbar sync propagates the pan

    def _push(self):
        if self._syncing:
            return
        for p in self._peers:
            p._pull(self)

    def _pull(self, src: "PdfGraphicsView"):
        self._syncing = True
        try:
            self.setTransform(src.transform())
            self._zoom = src._zoom
            self.horizontalScrollBar().setValue(src.horizontalScrollBar().value())
            self.verticalScrollBar().setValue(src.verticalScrollBar().value())
        finally:
            self._syncing = False

    def resizeEvent(self, e):
        super().resizeEvent(e)


class ContinuousDocView(QGraphicsView):
    """All pages, one continuous scroller: vertical flow, gap, autowrap grid.

    Zooming out reflows to as many columns as fit the window width
    (designer ruling §26). Peer-linked zoom/scroll like PdfGraphicsView.
    """

    GAP = 24

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._base: list[QPixmap] = []
        self._items: list[QGraphicsPixmapItem] = []
        self._zoom = 1.0
        self._did_fit = False
        self._peers: list["ContinuousDocView"] = []
        self._syncing = False
        self._current = 0
        self.pageChanged = None  # callback(index): status + minis
        self.changed = None  # callback(): any zoom/scroll/layout change (mini reframe)
        self.relayouted = None  # callback(): grid reflowed (mini reframe, §48)
        self.verticalScrollBar().valueChanged.connect(self._on_vscroll)
        self.horizontalScrollBar().valueChanged.connect(lambda _v: self._push())

    def link(self, other: "ContinuousDocView"):
        if other is not self and other not in self._peers:
            self._peers.append(other)

    @property
    def page_count(self) -> int:
        return len(self._items)

    @property
    def current_page(self) -> int:
        return self._current

    def page_pos(self, i: int) -> QPointF:
        """Scene position (top-left) of page i's image, for navigator mapping."""
        if 0 <= i < len(self._items):
            return self._items[i].pos()
        return QPointF(0, 0)

    def set_pages(self, images: list[QImage]):
        self._scene.clear()
        self._base = [QPixmap.fromImage(im) for im in images]
        self._items = []
        for pm in self._base:
            it = QGraphicsPixmapItem(pm)
            self._scene.addItem(it)
            self._items.append(it)
        self._zoom = 1.0
        self.resetTransform()
        self._current = 0
        self._did_fit = False
        self.relayout()
        self.verticalScrollBar().setValue(0)

    def _page_w(self) -> int:
        return max([pm.width() for pm in self._base], default=0)

    def _page_h(self) -> int:
        return max([pm.height() for pm in self._base], default=0)

    def cols(self) -> int:
        vw = max(1, self.viewport().width())
        slot = self._page_w() * self._zoom + self.GAP
        return max(1, int(vw / slot)) if slot > 0 else 1

    def relayout(self):
        if not self._items:
            return
        cols = self.cols()
        pw, ph = self._page_w(), self._page_h()
        for i, it in enumerate(self._items):
            r, c = divmod(i, cols)
            it.setPos(c * (pw + self.GAP), r * (ph + self.GAP))
        rows = (len(self._items) + cols - 1) // cols
        self.setSceneRect(0, 0, cols * (pw + self.GAP) - self.GAP,
                          rows * (ph + self.GAP) - self.GAP)
        self._notify_changed()
        if self.relayouted is not None:
            self.relayouted()

    def fit_width(self):
        if self._page_w():
            vw = max(1, self.viewport().width())
            self._zoom = max(0.05, vw / (self._page_w() + self.GAP))
            self.setTransform(QTransform().scale(self._zoom, self._zoom))
        self.relayout()
        self._push()

    def set_zoom(self, z: float):
        self._zoom = min(4.0, max(0.05, z))
        self.setTransform(QTransform().scale(self._zoom, self._zoom))
        self.relayout()
        self._push()

    def wheelEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            dy = e.angleDelta().y()
            self.set_zoom(self._zoom * (1.25 if dy > 0 else 1 / 1.25))
            e.accept()
        else:
            super().wheelEvent(e)  # page scroll; scrollbar sync propagates

    def _push(self):
        if self._syncing:
            return
        for p in self._peers:
            p._pull(self)
        self._notify_changed()

    def _notify_changed(self):
        if self.changed is not None:
            self.changed()

    def _pull(self, src: "ContinuousDocView"):
        self._syncing = True
        try:
            self.setTransform(src.transform())
            self._zoom = src._zoom
            self.horizontalScrollBar().setValue(src.horizontalScrollBar().value())
            self.verticalScrollBar().setValue(src.verticalScrollBar().value())
        finally:
            self._syncing = False

    def _on_vscroll(self, _v):
        self._push()
        self._update_current()

    def _update_current(self):
        if not self._items:
            return
        y = self.mapToScene(QPoint(0, 0)).y()
        stride = self._page_h() + self.GAP
        row = max(0, int(y / stride)) if stride else 0
        idx = min(len(self._items) - 1, row * self.cols())
        if idx != self._current:
            self._current = idx
            if self.pageChanged is not None:
                self.pageChanged(idx)

    def goto_page(self, i: int):
        if not self._items:
            return
        i = max(0, min(len(self._items) - 1, i))
        changed = (i != self._current)
        stride = self._page_h() + self.GAP
        self.verticalScrollBar().setValue(int((i // self.cols()) * stride * self._zoom))
        self._current = i
        if changed and self.pageChanged is not None:
            self.pageChanged(i)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._items and not self._did_fit and self.viewport().width() > 100:
            self._did_fit = True
            self.fit_width()
        else:
            self.relayout()
