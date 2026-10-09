import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import fitz  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pdf_reducer.ui_qt.app import MainWindow  # noqa: E402
from pdf_reducer.ui_qt.jobs import cpu_cap, estimate_bytes, mini_for_preset  # noqa: E402
from pdf_reducer.ui_qt.jobs import render_gray  # noqa: E402

_app = QApplication.instance() or QApplication([])


def _three_pages(tmpdir):
    src = os.path.join(tmpdir, "m.pdf")
    d = fitz.open()
    for i in range(3):
        p = d.new_page(width=400, height=400)
        p.insert_text((50, 200), f"Mini test {i}")
    d.save(src)
    d.close()
    return src


def _wait_job(w, timeout=90):
    t0 = time.perf_counter()
    while w._job is not None and not w._job.isFinished():
        assert time.perf_counter() - t0 < timeout, "filter job hung"
        _app.processEvents()
        time.sleep(0.05)
    _app.processEvents()


def test_background_job_fills_minis_and_preview(tmp_path):
    w = MainWindow(str(_three_pages(str(tmp_path))))
    assert w.before.page_count == 3
    _wait_job(w)
    assert w.after.page_count == 3  # preview applied without freezing
    assert w.filters.count() == 7  # passthrough/Original has no mini (§30)
    for i in range(7):
        assert not w.filters.item(i).icon().isNull(), i
    assert len(w._mini_est) == 7
    assert all(v.startswith("est.") for v in w._mini_est.values())


def test_pure_job_helpers():
    assert cpu_cap() >= 1
    gray = render_gray("examples/images.pdf", 0, 150)
    assert gray.ndim == 2
    from pdf_reducer.ui_qt.jobs import to_mini, crop_view
    mini = mini_for_preset(to_mini(crop_view(gray, None)), "bw-otsu")
    assert mini.shape == to_mini(gray).shape
    n = estimate_bytes("examples/images.pdf", 0, "bw-otsu", 300)
    assert n > 1000


def test_preset_strip_sync_by_id():
    import tempfile
    src = os.path.join(tempfile.mkdtemp(), "m.pdf")
    d = fitz.open()
    p = d.new_page(width=400, height=400)
    p.insert_text((50, 200), "Sync test")
    d.save(src)
    d.close()
    w = MainWindow(src)
    w.preset.setCurrentIndex(0)  # orig/passthrough: no strip row follows
    assert w.preset.itemData(0) == "orig"
    w._filterstrip_chosen(0)  # first mini -> bw-otsu preset
    from pdf_reducer.core import presets
    assert w.preset.itemData(w.preset.currentIndex()) == presets.PRESETS[1]["id"]


def test_file_menu_and_single_panel(tmp_path):
    w = MainWindow(str(_three_pages(str(tmp_path))))
    names = [a.text() for a in w.menuBar().actions()]
    assert "&File" in names and "&View" in names
    assert w.before.page_count == 3  # baseline renders synchronously
    _wait_job(w)
    assert w.after.page_count == 3  # preview arrives via background job
