"""Offscreen UI screenshots for designer review. All artifacts stay in ./.tmp/.

Usage: ./.venv/bin/python tools/shot.py [examples/images.pdf]
Captures: main window (side-h), stacked view, zoomed-out autowrap grid.
Filter jobs run in background; we wait for the latest generation to finish.
"""
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication  # noqa: E402
from pdf_reducer.ui_qt.app import MainWindow, setup_logging  # noqa: E402


def wait_job(w, timeout=120):
    t0 = time.perf_counter()
    while w._job is not None and not w._job.isFinished():
        if time.perf_counter() - t0 > timeout:
            print("WARN: job wait timed out")
            break
        app.processEvents()
        time.sleep(0.05)
    app.processEvents()


def main():
    setup_logging(True)
    global app
    app = QApplication([])
    pdf = sys.argv[1] if len(sys.argv) > 1 else "examples/images.pdf"
    w = MainWindow(pdf)
    w.resize(1100, 650)
    w.show()
    app.processEvents()

    wait_job(w)
    w.grab().save(".tmp/shot-main.png")
    print("shot: .tmp/shot-main.png")

    w.set_main_mode("stack-v")
    app.processEvents()
    w.grab().save(".tmp/shot-stacked.png")
    print("shot: .tmp/shot-stacked.png")

    w.set_main_mode("side-h")
    w.preset.setCurrentIndex(3)  # BW Strong T=210
    wait_job(w)
    w.before.set_zoom(0.35)  # zoomed out => autowrap grid
    app.processEvents()
    w.grab().save(".tmp/shot-preset.png")
    print("shot: .tmp/shot-preset.png")
    print("OK")


if __name__ == "__main__":
    main()
