"""Main window: continuous before/after panes, filter strip, ESC cancel."""
import logging
import os
import sys
import time
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QListView, QLabel, QSlider, QComboBox, QProgressBar,
    QFileDialog, QMessageBox, QSplitter, QCheckBox,
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtGui import QImage, QIcon, QPixmap, QPainter

from ..core.cancel import CancelToken
from ..core import pdf_io, threshold as T
from ..core import presets
from ..core.pipeline import process_file, recompress_file, gc_copy
from ..core.pdf_io import CancelledError
from .viewer import ContinuousDocView
from .overview import OverviewMap
from .jobs import FilterWorker, cpu_cap, pool as filter_pool

import fitz

log = logging.getLogger("pdf_reducer")

PREVIEW_DPI = 150


def setup_logging(debug: bool = False):
    """Stdout logging for run-and-review. INFO default; --debug => DEBUG + diagnostics."""
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S"))
    root = logging.getLogger("pdf_reducer")
    root.handlers.clear()
    root.addHandler(h)
    root.setLevel(logging.DEBUG if debug else logging.INFO)


def gray_to_qimage(gray: np.ndarray) -> QImage:
    h, w = gray.shape
    return QImage(gray.data, w, h, w, QImage.Format_Grayscale8).copy()


def bw_to_qimage(bw: np.ndarray) -> QImage:
    h, w = bw.shape
    return QImage(bw.data, w, h, w, QImage.Format_Grayscale8).copy()


def rgb_to_qimage(rgb: np.ndarray) -> QImage:
    h, w = rgb.shape[:2]
    return QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888).copy()


def fmt_bytes(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}MB"
    if n >= 1_000:
        return f"{n / 1_000:.0f}KB"
    return f"{n}B"


class Worker(QThread):
    done = Signal(str)
    failed = Signal(str)
    progressed = Signal(int, int)

    def __init__(self, in_path, out_path, spec: dict, token):
        super().__init__()
        self.args = (in_path, out_path, spec, token)

    def run(self):
        in_path, out_path, spec, token = self.args
        try:
            cb = lambda a, b: self.progressed.emit(a, b)  # noqa: E731
            if spec["mode"] == "bw":
                process_file(in_path, out_path, spec["strategy"], spec["t"], spec["dpi"], token,
                             page_size=spec["page_size"], force_raster=spec["force_raster"],
                             progress=cb)
            elif spec["mode"] == "color":
                recompress_file(in_path, out_path, spec["dpi_cap"], spec["jpeg_q"], token,
                                progress=cb)
            else:
                gc_copy(in_path, out_path)
            if token.cancelled:
                try:
                    os.unlink(out_path)
                except OSError:
                    pass
                self.failed.emit("Cancelled")
            else:
                self.done.emit(out_path)
        except CancelledError:
            try:
                os.unlink(out_path)
            except OSError:
                pass
            self.failed.emit("Cancelled")
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, start_pdf: str | None = None):
        super().__init__()
        self.setWindowTitle("pdf-reducer")
        self.resize(1100, 650)
        self.doc = None
        self.path = None
        self.token = CancelToken()
        self.worker: Worker | None = None
        self._gen = 0  # background filter-job generation (stale jobs abandoned)
        self._job = None
        self._jobs: set = set()  # in-flight workers: dropping the last ref while
        self._job_token = CancelToken()  # a QThread still runs aborts (Qt fatal)
        self._mini_cache: dict = {}  # pid -> mini array (latest generation)
        self._mini_est: dict = {}    # pid -> "est. X" (latest generation)
        self._applying = False  # True while a background preview is applied (no sync/cascade)
        self.setAcceptDrops(True)

        root = QWidget()
        self.setCentralWidget(root)
        top = QHBoxLayout(root)

        mid = QVBoxLayout()
        self.split = QSplitter(Qt.Horizontal)
        self.before = ContinuousDocView()  # baseline, all pages
        self.after = ContinuousDocView()   # selected filter, all pages
        self.before.link(self.after)  # designer ruling: panes always synced
        self.after.link(self.before)
        self.before.pageChanged = self._on_page_changed
        self.after.pageChanged = self._on_page_changed
        self.before.setToolTip("Baseline — original, unmodified")
        self.after.setToolTip("Filter preview — scroll=pan, ctrl+wheel=zoom, drag=pan")
        self.split.addWidget(self.before)
        self.split.addWidget(self.after)
        self.split.setStretchFactor(0, 1)
        self.split.setStretchFactor(1, 1)
        self.split.setSizes([550, 550])
        mid.addWidget(self.split, 1)
        self.filters = QListWidget()  # filter strip: live mini per filter
        self.filters.setViewMode(QListView.IconMode)
        self.filters.setIconSize(QSize(150, 170))
        self.filters.setResizeMode(QListView.Adjust)
        self.filters.setMovement(QListView.Static)
        self.filters.setSpacing(4)
        self.filters.setWordWrap(True)
        self.filters.setMaximumHeight(230)
        self.filters.setToolTip("Filters — click to preview (left stays baseline)")
        self._strip_ids = [p["id"] for p in presets.PRESETS if p["mode"] != "passthrough"]
        for pid in self._strip_ids:
            p = presets.get(pid)
            item = QListWidgetItem(p["label"])
            item.setData(Qt.UserRole, pid)
            item.setToolTip(p["blurb"])
            item.setSizeHint(QSize(150, 180))  # icon canvas carries name + est size
            self.filters.addItem(item)
        mid.addWidget(QLabel("Filters (left stays baseline, right shows filter):"))
        mid.addWidget(self.filters)

        right = QVBoxLayout()
        self.preset = QComboBox()
        for p in presets.PRESETS:
            self.preset.addItem(p["label"], p["id"])
        self.preset.setCurrentIndex([p["id"] for p in presets.PRESETS].index(presets.default_preset_id()))
        self.strategy = QComboBox()
        self.strategy.addItems(["otsu", "simple", "adaptive", "sauvola"])
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 255)
        self.slider.setValue(180)
        self.t_label = QLabel("T=180")
        self.prev_btn = QPushButton("◀ Prev")
        self.next_btn = QPushButton("Next ▶")
        self.dpi = QComboBox()
        for d in presets.RASTER_DPIS:
            self.dpi.addItem(f"{d} dpi", d)
        self.dpi.setCurrentIndex(list(presets.RASTER_DPIS).index(presets.DEFAULT_DPI))
        self.page_size = QComboBox()
        for pid in presets.PAGE_SIZE_IDS:
            self.page_size.addItem(presets.PAGE_SIZE_LABELS[pid], pid)
        self.page_size.setCurrentIndex(list(presets.PAGE_SIZE_IDS).index(presets.DEFAULT_PAGE_SIZE))
        self.force_raster = QCheckBox("Force full-page raster")
        self.force_raster.setChecked(True)
        self.force_raster.setToolTip("ON: every page flattened to one image (default). OFF: pages with extractable text pass through untouched.")
        self.nav = OverviewMap()
        self.nav.navigate = self._nav_goto
        self.save_btn = QPushButton("Save reduced…")
        self.cancel_btn = QPushButton("Cancel (ESC)")
        self._nav_img = None
        self._nav_page = -1
        right.addWidget(QLabel("Preset:"))
        right.addWidget(self.preset)
        right.addWidget(QLabel("Strategy:"))
        right.addWidget(self.strategy)
        right.addWidget(self.t_label)
        right.addWidget(self.slider)
        right.addWidget(QLabel("Raster DPI:"))
        right.addWidget(self.dpi)
        right.addWidget(QLabel("Page size:"))
        right.addWidget(self.page_size)
        right.addWidget(self.force_raster)
        right.addWidget(QLabel("Navigator (original):"))
        right.addWidget(self.nav)
        right.addWidget(self.prev_btn)
        right.addWidget(self.next_btn)
        right.addWidget(self.save_btn)
        right.addWidget(self.cancel_btn)
        right.addStretch(1)

        top.addLayout(mid, 7)
        top.addLayout(right, 3)

        self.page_label = QLabel("No document")
        self.status = QLabel("Drop a PDF here or Open… (File > Open)")
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        sb = self.statusBar()
        sb.addWidget(self.status, 1)
        sb.addPermanentWidget(self.page_label)
        sb.addPermanentWidget(self.progress)

        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(200)
        self._preview_timer.timeout.connect(self._dispatch_filters)
        self._mini_timer = QTimer(self)
        self._mini_timer.setSingleShot(True)
        self._mini_timer.setInterval(250)
        self._mini_timer.timeout.connect(self._dispatch_filters)

        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.cancel)
        self.before.changed = self._refresh_nav
        self.slider.valueChanged.connect(lambda v: (self.t_label.setText(f"T={v}"), self._preview_timer.start()))
        self.strategy.currentTextChanged.connect(lambda _: self._preview_timer.start())
        self.prev_btn.clicked.connect(lambda: self.before.goto_page(self.before.current_page - 1))
        self.next_btn.clicked.connect(lambda: self.before.goto_page(self.before.current_page + 1))
        self.preset.currentIndexChanged.connect(self._preset_chosen)
        self.filters.currentRowChanged.connect(self._filterstrip_chosen)

        filem = self.menuBar().addMenu("&File")
        open_act = filem.addAction("Open…")
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self.open_dialog)
        save_act = filem.addAction("Save reduced…")
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.save)
        quit_act = filem.addAction("Quit")
        quit_act.setShortcut("Ctrl+Q")
        quit_act.triggered.connect(self.close)
        view = self.menuBar().addMenu("&View")
        main_menu = view.addMenu("&Main panes")
        self._main_actions = {}
        for label, mode in [("Side by side (H)  Ctrl+1", "side-h"),
                            ("Stacked (V)  Ctrl+2", "stack-v"),
                            ("Single (toggle)  Ctrl+3", "single")]:
            a = main_menu.addAction(label)
            a.setCheckable(True)
            a.triggered.connect(lambda _=False, m=mode: self.set_main_mode(m))
            self._main_actions[mode] = a
        filt_menu = view.addMenu("&Filter thumbnails")
        self._filter_actions = {}
        for label, mode in [("Filmstrip (H)", "film-h"), ("Rail (V)", "rail-v"), ("Grid", "grid")]:
            a = filt_menu.addAction(label)
            a.setCheckable(True)
            a.triggered.connect(lambda _=False, m=mode: self.set_filter_mode(m))
            self._filter_actions[mode] = a
        self.set_main_mode("side-h")
        self.set_filter_mode("film-h")

        # ESC anywhere cancels
        self.cancel_shortcut = self.cancel_btn  # button doubles as action
        if start_pdf:
            self.open_file(start_pdf)

    # --- presets + view modes ---
    def _preset_chosen(self, idx: int):
        pid = self.preset.itemData(idx)
        if not pid:
            return
        log.info("preset selected: %s", pid)
        p = presets.get(pid)
        if p["mode"] == "bw":
            self.strategy.setCurrentText(p["params"]["strategy"])
            self.slider.setValue(p["params"]["t"])
        if pid in self._strip_ids:  # passthrough has no mini; left pane is the baseline
            row = self._strip_ids.index(pid)
            if self.filters.currentRow() != row:
                self.filters.setCurrentRow(row)
        self._preview_timer.start()

    def _filterstrip_chosen(self, row: int):
        if row < 0 or row >= len(self._strip_ids):
            return
        idx = [p["id"] for p in presets.PRESETS].index(self._strip_ids[row])
        if self.preset.currentIndex() != idx:
            self.preset.setCurrentIndex(idx)
        else:
            self._preview_timer.start()

    def set_main_mode(self, mode: str):
        log.info("view main mode: %s", mode)
        for m, a in self._main_actions.items():
            a.setChecked(m == mode)
        if mode == "side-h":
            self.split.setOrientation(Qt.Horizontal)
            self.before.show()
            self.after.show()
        elif mode == "stack-v":
            self.split.setOrientation(Qt.Vertical)
            self.before.show()
            self.after.show()
        else:  # single: preview only, maximized
            self.split.setOrientation(Qt.Horizontal)
            self.before.hide()
            self.after.show()
        self._main_mode = mode

    def set_filter_mode(self, mode: str):
        log.info("view filter mode: %s", mode)
        for m, a in self._filter_actions.items():
            a.setChecked(m == mode)
        if mode == "film-h":
            self.filters.setFlow(QListWidget.LeftToRight)
            self.filters.setMaximumHeight(230)
            self.filters.setMinimumHeight(190)
        elif mode == "rail-v":
            self.filters.setFlow(QListWidget.TopToBottom)
            self.filters.setMaximumHeight(16777215)
        else:  # grid
            self.filters.setFlow(QListWidget.LeftToRight)
            self.filters.setMaximumHeight(16777215)
            self.filters.setWrapping(True)
            return
        self.filters.setWrapping(False)

    # --- DnD / open ---
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for u in e.mimeData().urls():
            p = u.toLocalFile()
            if p.lower().endswith(".pdf"):
                log.info("dnd opened: %s", p)
                self.open_file(p)
                return

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.cancel()
        elif e.key() == Qt.Key_PageDown:
            self.next_btn.click()
        elif e.key() == Qt.Key_PageUp:
            self.prev_btn.click()
        else:
            super().keyPressEvent(e)

    def open_dialog(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF (*.pdf)")
        if p:
            self.open_file(p)

    def open_file(self, path: str):
        try:
            if self.doc:
                self.doc.close()
            self.doc = fitz.open(path)
            self.path = path
            self._mini_cache.clear()
            self._mini_est.clear()
            self._render_all()
            self.before.goto_page(0)
            self.page_label.setText(f"Page 1 of {self.doc.page_count} (PgUp/PgDn)")
            self._nav_page = -1
            self._nav_img = None
            self._refresh_nav()
            self.status.setText(f"{os.path.basename(path)} — {self.doc.page_count} pages")
            log.info("opened %s pages=%d", path, self.doc.page_count)
        except Exception as e:  # noqa: BLE001
            log.warning("open failed %s: %s", path, e)
            QMessageBox.warning(self, "Open failed", str(e))

    # --- continuous render ---
    def _render_page_rgb(self, i: int, dpi: int = PREVIEW_DPI) -> np.ndarray:
        pix = self.doc[i].get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).copy()

    def _render_page_gray(self, i: int, dpi: int = PREVIEW_DPI) -> np.ndarray:
        pix = self.doc[i].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()

    def _render_all(self):
        """Baseline panes (fast sync renders) + background filter job."""
        if not self.doc:
            return
        t0 = time.perf_counter()
        n = self.doc.page_count
        self.before.set_pages([rgb_to_qimage(self._render_page_rgb(i)) for i in range(n)])
        log.info("baseline rendered %d pages in %.0fms", n, (time.perf_counter() - t0) * 1000)
        self._dispatch_filters()

    def _active_spec(self) -> dict:
        pid = self.preset.itemData(self.preset.currentIndex())
        p = presets.get(pid)
        spec = {"preset_id": pid, "mode": p["mode"], "dpi": self.dpi.currentData()}
        if p["mode"] == "bw":
            spec.update(strategy=self.strategy.currentText(), t=self.slider.value())
        return spec

    def _viewport_crop(self):
        """Current viewport in baseline-render pixels + page index for job minis."""
        i = self.before.current_page
        origin = self.before.page_pos(i)
        vis = self.before.mapToScene(self.before.viewport().rect()).boundingRect()
        rel = vis.translated(-origin.x(), -origin.y())
        return i, (rel.x(), rel.y(), rel.width(), rel.height())

    def _dispatch_filters(self):
        """Full per-preset processing in background; stale jobs abandoned by gen."""
        if not self.doc:
            return
        self._gen += 1
        self._job_token.cancel()
        self._job_token = CancelToken()
        i, crop = self._viewport_crop()
        spec = self._active_spec()
        filter_pool()  # warm on the main thread; workers only ever submit
        self.status.setText(f"Rendering filters… (job {self._gen})")
        log.info("filter job gen=%d page=%d preset=%s workers<=%d viewport=%s",
                 self._gen, i + 1, spec["preset_id"], cpu_cap(),
                 tuple(int(v) for v in crop))
        job = FilterWorker(self.path, i, crop, self._strip_ids, spec,
                           self._job_token, self._gen)
        job.mini_done.connect(self._jm_mini)
        job.est_done.connect(self._jm_est)
        job.preview_done.connect(self._jm_preview)
        job.progressed.connect(self._jm_progress)
        job.finished.connect(lambda: self._clear_job(job))
        self._job = job
        self._jobs.add(job)
        job.start()

    def _clear_job(self, job):
        self._jobs.discard(job)
        if self._job is job:
            self._job = None

    def _paint_strip_item(self, pid: str):
        if pid not in self._strip_ids or pid not in self._mini_cache:
            return
        arr = self._mini_cache[pid]
        q = gray_to_qimage(arr) if arr.ndim == 2 else rgb_to_qimage(arr)
        est = self._mini_est.get(pid, "…")
        icon = QPixmap(150, 170)
        icon.fill(Qt.white)
        pt = QPainter(icon)
        mini = QPixmap.fromImage(q).scaled(120, 118, Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation)
        pt.drawPixmap((150 - mini.width()) // 2, 0, mini)
        pt.drawText(0, 120, 150, 50, Qt.AlignHCenter | Qt.TextWordWrap,
                    f"{presets.get(pid)['label']}\n{est}")
        pt.end()
        self.filters.item(self._strip_ids.index(pid)).setIcon(QIcon(icon))
        self.filters.item(self._strip_ids.index(pid)).setText("")

    def _jm_mini(self, pid, arr, gen):
        if gen != self._gen:
            return
        self._mini_cache[pid] = arr
        self._paint_strip_item(pid)

    def _jm_est(self, pid, text, gen):
        if gen != self._gen:
            return
        self._mini_est[pid] = text
        self._paint_strip_item(pid)
        log.debug("job gen=%d %s -> %s", gen, pid, text)

    def _jm_preview(self, pages, gen):
        if gen != self._gen or not self.doc:
            return
        keep_h = self.after.horizontalScrollBar().value()
        keep_v = self.after.verticalScrollBar().value()
        self._applying = True
        self.after._syncing = True
        try:
            self.after.set_pages([rgb_to_qimage(a) for a in pages])
            self.after.setTransform(self.before.transform())
            self.after._zoom = self.before._zoom
            self.after.relayout()
            self.after.horizontalScrollBar().setValue(keep_h)
            self.after.verticalScrollBar().setValue(keep_v)
        finally:
            self.after._syncing = False
            self._applying = False
        self.status.setText(f"{os.path.basename(self.path)} — {self.doc.page_count} pages")
        log.info("job gen=%d preview applied (%d pages)", gen, len(pages))

    def _jm_progress(self, done, total, gen):
        if gen != self._gen:
            return
        self.progress.setMaximum(total)
        self.progress.setValue(done)
        log.debug("job gen=%d filter progress %d/%d", gen, done, total)

    def _on_page_changed(self, idx: int):
        if not self.doc or getattr(self, "_applying", False):
            return
        self.page_label.setText(f"Page {idx + 1} of {self.doc.page_count} (PgUp/PgDn)")
        log.debug("current page %d", idx + 1)
        self._mini_timer.start()  # debounced background filter job

    def _refresh_nav(self):
        """Repaint the navigator: baseline page + current viewport rect."""
        if not self.doc:
            return
        i = self.before.current_page
        if i != self._nav_page or self._nav_img is None:
            self._nav_img = rgb_to_qimage(self._render_page_rgb(i))
            self._nav_page = i
            self.nav.set_page(self._nav_img)
        origin = self.before.page_pos(i)
        visible = self.before.mapToScene(self.before.viewport().rect()).boundingRect()
        self.nav.set_view(visible, origin)

    def _nav_goto(self, pt):
        """Navigator click (baseline page coords) -> center main view there."""
        if not self.doc:
            return
        i = self._nav_page
        o = self.before.page_pos(i)
        self.before.centerOn(o + pt)
        self.before._push()
        log.info("navigator jump page=%d", i + 1)

    # --- run / cancel ---
    def save(self):
        if not self.path:
            return
        out, _ = QFileDialog.getSaveFileName(self, "Save reduced PDF", self.path.replace(".pdf", ".reduced.pdf"), "PDF (*.pdf)")
        if not out:
            return
        if os.path.abspath(out) == os.path.abspath(self.path):
            QMessageBox.warning(self, "Refusing", "Won't overwrite input. Pick another name.")
            return
        self.token.reset()
        pid = self.preset.itemData(self.preset.currentIndex())
        p = presets.get(pid)
        if p["mode"] == "bw":
            spec = {"mode": "bw", "strategy": self.strategy.currentText(), "t": self.slider.value(),
                    "dpi": self.dpi.currentData(), "page_size": self.page_size.currentData(),
                    "force_raster": self.force_raster.isChecked()}
        elif p["mode"] == "color":
            spec = {"mode": "color", "dpi_cap": p["params"]["dpi_cap"], "jpeg_q": p["params"]["jpeg_q"]}
        else:
            spec = {"mode": "passthrough"}
        log.info("save start preset=%s spec=%s in=%s out=%s", pid, spec, self.path, out)
        self.worker = Worker(self.path, out, spec, self.token)
        self._jobs.add(self.worker)
        self.worker.finished.connect(lambda: self._jobs.discard(self.worker))
        self.worker.done.connect(self._on_done)
        self.worker.failed.connect(self._on_failed)
        self.worker.progressed.connect(self._on_progress)
        self.worker.start()
        self.status.setText("Working… ESC to cancel")

    def _on_done(self, path: str):
        log.info("saved %s", path)
        self.status.setText(f"Saved {path}")

    def _on_failed(self, msg: str):
        log.info("job ended: %s", msg)
        self.status.setText(msg)

    def _on_progress(self, a: int, b: int):
        self.progress.setMaximum(b)
        self.progress.setValue(a)
        log.debug("progress page %d/%d", a, b)

    def cancel(self):
        log.info("cancel requested by designer (ESC/button)")
        self.token.cancel()
        self.status.setText("Cancelling…")


def main(start_pdf: str | None = None, debug: bool = False):
    log.info("starting pdf-reducer debug=%s pdf=%s", debug, start_pdf)
    if debug:
        try:
            from PySide6 import __version__ as pyside_v
        except Exception:  # noqa: BLE001
            pyside_v = "?"
        from PySide6.QtCore import qVersion
        log.debug("env python=%s pyside=%s qt=%s fitz=%s cwd=%s",
                  sys.version.split()[0], pyside_v, qVersion(),
                  getattr(fitz, "VersionBind", "?"), os.getcwd())
        log.debug("argv=%s", sys.argv)
        log.debug("filter workers<=%d (half cores cap)", cpu_cap())
    app = QApplication(sys.argv)
    w = MainWindow(start_pdf)
    w.show()
    log.info("window shown")
    sys.exit(app.exec())
