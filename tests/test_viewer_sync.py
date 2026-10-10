import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pdf_minimalist.ui_qt.viewer import PdfGraphicsView  # noqa: E402

_app = QApplication.instance() or QApplication([])


def _big_img():
    img = QImage(2000, 2600, QImage.Format_Grayscale8)
    img.fill(128)
    return img


def test_panes_stay_synced():
    a, b = PdfGraphicsView(), PdfGraphicsView()
    a.resize(300, 300)
    b.resize(300, 300)
    a.link(b)
    b.link(a)
    a.set_image(_big_img())
    b.set_image(_big_img())
    # zoom one -> other follows
    a.scale(2.0, 2.0)
    a._zoom = 2.0
    a._push()
    assert b.transform() == a.transform()
    assert b._zoom == a._zoom
    # pan one (scrollbar) -> other follows
    b.verticalScrollBar().setValue(b.verticalScrollBar().maximum())
    assert a.verticalScrollBar().value() == b.verticalScrollBar().value()


def _wheel(mod, dy=120):
    from PySide6.QtCore import QPoint, QPointF
    from PySide6.QtGui import QWheelEvent
    return QWheelEvent(QPointF(150, 150), QPointF(150, 150), QPoint(0, 0), QPoint(0, dy),
                       Qt.MouseButton.NoButton, mod, Qt.ScrollPhase.NoScrollPhase, False)


def test_ctrl_wheel_zooms_plain_wheel_scrolls():
    a, b = PdfGraphicsView(), PdfGraphicsView()
    a.resize(300, 300)
    b.resize(300, 300)
    a.link(b)
    b.link(a)
    a.set_image(_big_img())
    b.set_image(_big_img())
    t0 = a.transform().m11()
    a.wheelEvent(_wheel(Qt.KeyboardModifier.ControlModifier))
    assert a.transform().m11() > t0  # zoomed in
    assert b.transform() == a.transform()  # peer synced
    v0 = a.verticalScrollBar().value()
    a.wheelEvent(_wheel(Qt.KeyboardModifier.NoModifier, dy=-120))
    assert a.verticalScrollBar().value() > v0  # scrolled, not zoomed
    assert b.verticalScrollBar().value() == a.verticalScrollBar().value()
