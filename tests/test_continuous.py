import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402

from pdf_minimalist.ui_qt.viewer import ContinuousDocView  # noqa: E402
from pdf_minimalist.ui_qt.overview import OverviewMap  # noqa: E402

_app = QApplication.instance() or QApplication([])


def _shown(*views):
    for v in views:
        v.show()
    _app.processEvents()


def _pages(n=5, w=400, h=500):
    out = []
    for i in range(n):
        img = QImage(w, h, QImage.Format_Grayscale8)
        img.fill(100 + i * 10)
        out.append(img)
    return out


def test_autowrap_cols():
    a, b = ContinuousDocView(), ContinuousDocView()
    a.link(b)
    b.link(a)
    a.resize(900, 600)
    a.set_pages(_pages())
    _shown(a)
    assert a.page_count == 5
    assert a.cols() == 1  # fit-width default => single column
    a.set_zoom(0.4)  # zoom out => autowrap grid
    assert a.cols() >= 2
    a.set_zoom(4.0)  # zoom in => single column
    assert a.cols() == 1


def test_continuous_zoom_scroll_synced():
    a, b = ContinuousDocView(), ContinuousDocView()
    a.resize(400, 600)
    b.resize(400, 600)
    a.link(b)
    b.link(a)
    a.set_pages(_pages())
    b.set_pages(_pages())
    _shown(a, b)
    a.set_zoom(2.0)
    assert b._zoom == a._zoom
    a.goto_page(4)
    assert a.current_page == 4
    assert b.verticalScrollBar().value() == a.verticalScrollBar().value()
    a.goto_page(99)
    assert a.current_page == 4  # clamped


def test_overview_mirrors_view():
    from PySide6.QtCore import QPointF, QRectF
    nav = OverviewMap()
    nav.resize(200, 200)
    nav.show()
    _app.processEvents()
    img = _pages(n=1)[0]
    nav.set_page(img)
    nav.set_view(QRectF(50, 60, 100, 120), QPointF(0, 0))
    assert not nav._rect.isNull()
    hits = []
    nav.navigate = lambda pt: hits.append((pt.x(), pt.y()))
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent, QPointF as PF
    ev = QMouseEvent(QEvent.Type.MouseButtonPress, PF(100, 100), PF(100, 100),
                     Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                     Qt.KeyboardModifier.NoModifier)
    nav.mousePressEvent(ev)
    assert len(hits) == 1
    assert not nav.grab().isNull()
