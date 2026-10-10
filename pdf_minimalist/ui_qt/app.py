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
from PySide6.QtGui import QImage, QIcon, QPixmap, QPainter, QFont, QPen

from ..core.cancel import CancelToken
from ..core import pdf_io, threshold as T
from ..core import presets
from ..core.pipeline import process_file, recompress_file, gc_copy
from ..core.pdf_io import CancelledError
from .viewer import ContinuousDocView
from .jobs import FilterWorker, cpu_cap, pool as filter_pool, frame_view

import fitz

log = logging.getLogger("pdf_minimalist")

PREVIEW_DPI = 150


def setup_logging(debug: bool = False):
    """Stdout logging for run-and-review. INFO default; --debug => DEBUG + diagnostics."""
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S"))
    root = logging.getLogger("pdf_minimalist")
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


def _preset_algo(pid: str) -> str:
    """One-line filter recipe for the strip caption (§53): the image
    algorithm each mini was rendered with — threshold strategy (+T for the
    fixed-threshold filter), render DPI and encoder for BW; JPEG quality and
    DPI cap for color."""
    p = presets.get(pid)
    prm = p["params"]
    if p["mode"] == "bw":
        base = f"{prm['strategy']} T{prm['t']}" if prm["strategy"] == "simple" \
            else prm["strategy"]
        return f"{base} · {prm['dpi']}dpi · JBIG2"
    if p["mode"] == "color":
        return f"JPEG q{prm['jpeg_q']} · ≤{prm['dpi_cap']}dpi"
    if p["mode"] == "jpx":
        return f"JPEG2000 r{prm.get('rate', 24)} · ≤{prm['dpi_cap']}dpi"
    return "as-is"


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
            elif spec["mode"] == "jpx":
                recompress_file(in_path, out_path, spec["dpi_cap"], token=token,
                                progress=cb, codec="jpx", rate=spec["rate"])
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
        self.setWindowTitle("pdf-minimalist")
        self.resize(1100, 650)
        self.doc = None
        self.path = None
        self.token = CancelToken()
        self.worker: Worker | None = None
        self._gen = 0  # background filter-job generation (stale jobs abandoned)
        self._job = None
        self._jobs: set = set()  # in-flight workers: dropping the last ref while
        self._job_token = CancelToken()  # a QThread still runs aborts (Qt fatal)
        self._mini_pages: dict = {}  # (file_key, pid) -> [mini-page array|None] (§48)
        self._est_bytes: dict = {}  # (file_key, pid, dpi) -> [int|None], BW pages (§55)
        self._est_doc: dict = {}  # (file_key, pid) -> int doc total, color (§59)
        self._mini_view: dict = {}  # pid -> exact-view composite for today (§48)
        self._mini_est: dict = {}    # pid -> "est. X" for the top-visible page
        self._filter_prog: dict = {}  # pid -> 0.0..1.0 per-filter progress (§43)
        self._preview_cache: dict = {}  # (file_key, spec_tuple) -> [arrays] (§44)
        self._expect: dict = {}  # pid -> [mini_done, mini_total, est_done, est_total]
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
        self.filters.setIconSize(QSize(150, 190))
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
            item.setSizeHint(QSize(150, 200))  # icon canvas: box + 3-line caption
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
        self.save_btn = QPushButton("Save reduced…")
        self.cancel_btn = QPushButton("Cancel (ESC)")
        right.addWidget(QLabel("Preset:"))
        right.addWidget(self.preset)
        # §54: filter details readout — the active filter's full recipe.
        self.details = QLabel()
        self.details.setWordWrap(True)
        self.details.setStyleSheet("QLabel { background: palette(base); "
                                   "border: 1px solid palette(mid); padding: 4px; }")
        right.addWidget(QLabel("Filter details:"))
        right.addWidget(self.details)
        right.addWidget(QLabel("Strategy:"))
        right.addWidget(self.strategy)
        right.addWidget(self.t_label)
        right.addWidget(self.slider)
        right.addWidget(QLabel("Raster DPI:"))
        right.addWidget(self.dpi)
        right.addWidget(QLabel("Page size:"))
        right.addWidget(self.page_size)
        right.addWidget(self.force_raster)
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
        # §47/§48: view changes (scroll/pan/zoom/resize/page) only REFRAME
        # minis from cache — they never dispatch. Debounced: one reframe max
        # per settle, no matter how many scroll ticks arrived.
        self._reframe_timer = QTimer(self)
        self._reframe_timer.setSingleShot(True)
        self._reframe_timer.setInterval(150)
        self._reframe_timer.timeout.connect(self._reframe_minis)

        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.cancel)
        self.before.changed = self._on_view_changed
        self.before.relayouted = self._reframe_timer.start
        self.after.relayouted = self._reframe_timer.start
        self.slider.valueChanged.connect(lambda v: (self.t_label.setText(f"T={v}"), self._refresh_details(), self._preview_timer.start()))
        self.strategy.currentTextChanged.connect(lambda _: (self._refresh_details(), self._preview_timer.start()))
        self.dpi.currentIndexChanged.connect(lambda _: (self._refresh_details(), self._preview_timer.start()))
        self.page_size.currentIndexChanged.connect(lambda _: (self._refresh_details(), self._preview_timer.start()))
        self.force_raster.toggled.connect(lambda _: (self._refresh_details(), self._preview_timer.start()))
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
        self._refresh_details()
        if start_pdf:
            self.open_file(start_pdf)

    # --- presets + view modes ---
    def _refresh_details(self):
        """Right-panel readout of the active filter's full recipe (§54)."""
        pid = self.preset.itemData(self.preset.currentIndex())
        if not pid:
            return
        p = presets.get(pid)
        if p["mode"] == "bw":
            lines = [
                f"Threshold: {self.strategy.currentText()} "
                f"T={self.slider.value()}",
                f"Render: {self.dpi.currentData()} dpi · "
                f"{presets.PAGE_SIZE_LABELS[self.page_size.currentData()]} · "
                f"{'forced raster' if self.force_raster.isChecked() else 'text pass-through'}",
                "Encode: JBIG2",
            ]
        elif p["mode"] == "color":
            prm = p["params"]
            lines = [
                f"Recompress: JPEG q={prm['jpeg_q']} · ≤{prm['dpi_cap']}dpi",
                "Vectors and text preserved",
            ]
        elif p["mode"] == "jpx":
            prm = p["params"]
            lines = [
                f"Recompress: JPEG2000 r={prm.get('rate', 24)} · ≤{prm['dpi_cap']}dpi",
                "Vectors and text preserved",
            ]
        else:
            lines = ["gc + deflate only — pixels unchanged"]
        self.details.setText("\n".join(lines))

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
        self._refresh_details()
        if self._try_apply_cached():
            return
        self._preview_timer.start()

    def _filterstrip_chosen(self, row: int):
        if row < 0 or row >= len(self._strip_ids):
            return
        idx = [p["id"] for p in presets.PRESETS].index(self._strip_ids[row])
        if self.preset.currentIndex() != idx:
            self.preset.setCurrentIndex(idx)
        elif self._try_apply_cached():
            return
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
        elif e.modifiers() & Qt.ControlModifier and e.key() in (
                Qt.Key_Plus, Qt.Key_Equal, Qt.Key_Minus, Qt.Key_0):
            # §52: modern standard keyboard zoom — Ctrl+Plus in, Ctrl+Minus
            # out, Ctrl+0 fit. (Plus and Equal share the = key on US layouts.)
            self._keyboard_zoom(e.key())
        else:
            super().keyPressEvent(e)

    def _keyboard_zoom(self, key):
        """Apply one keyboard-zoom step to the synced panes (§52)."""
        if not self.doc:
            return
        if key in (Qt.Key_Plus, Qt.Key_Equal):
            self.before.set_zoom(self.before._zoom * 1.25)
            log.info("keyboard zoom in (Ctrl+Plus)")
        elif key == Qt.Key_Minus:
            self.before.set_zoom(self.before._zoom / 1.25)
            log.info("keyboard zoom out (Ctrl+Minus)")
        elif key == Qt.Key_0:
            self.before.fit_width()
            log.info("keyboard zoom reset (Ctrl+0)")

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
            self._mini_pages.clear()
            self._est_bytes.clear()
            self._est_doc.clear()
            self._mini_view.clear()
            self._mini_est.clear()
            self._filter_prog.clear()
            self._expect.clear()
            self._preview_cache.clear()
            for pid in self._strip_ids:
                self._filter_prog[pid] = 0.0
            self._repaint_all_strip()
            self._render_all()
            self.before.goto_page(0)
            self.page_label.setText(f"Page 1 of {self.doc.page_count} (PgUp/PgDn)")
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

    def _file_key(self):
        """Identity for process-once cache §44: path + mtime + size."""
        if not self.path:
            return None
        try:
            st = os.stat(self.path)
            return (os.path.abspath(self.path), st.st_mtime_ns, st.st_size)
        except OSError:
            return (os.path.abspath(self.path),)

    @staticmethod
    def _spec_tuple(spec: dict):
        return (spec.get("preset_id"), spec.get("mode"), spec.get("dpi"),
                spec.get("strategy"), spec.get("t"))

    def _repaint_all_strip(self):
        for pid in self._strip_ids:
            self._paint_strip_item(pid)

    def _apply_preview_pages(self, pages, source: str):
        """Show preview pages in the right pane, preserving scroll/zoom."""
        if not self.doc:
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
        self.status.setText(f"{os.path.basename(self.path)} — {self.doc.page_count} pages ({source})")
        log.info("preview applied from %s (%d pages)", source, len(pages))

    def _try_apply_cached(self) -> bool:
        """§44: if the active spec already has a cached preview, show it now."""
        if not self.doc or not self.path:
            return False
        fkey = self._file_key()
        if fkey is None:
            return False
        spec = self._active_spec()
        pkey = (fkey, self._spec_tuple(spec))
        pages = self._preview_cache.get(pkey)
        if pages is None:
            return False
        try:
            self._preview_timer.stop()
        except Exception:
            pass
        self._apply_preview_pages(pages, "cache")
        return True

    def _dispatch_filters(self):
        """Background work for cache misses only (§§43/44/47/48).

        Dispatches on FILE change or SPEC change alone. Scroll, pan, zoom,
        page turns and strip clicks never reach here with work to do: minis
        reframe from the per-preset caches (§48) and previews hit
        `_try_apply_cached` first. A click whose 150dpi preview was never
        built dispatches a preview-only job — once per (file, spec), ever.
        """
        if not self.doc or not self.path:
            return
        fkey = self._file_key()
        if fkey is None:
            return
        n = self.doc.page_count
        spec = self._active_spec()
        spec_tup = self._spec_tuple(spec)
        dpi = spec.get("dpi")
        preview_key = (fkey, spec_tup)

        need_mini = {}
        for pid in self._strip_ids:
            pages = self._mini_pages.get((fkey, pid))
            if pages is None:
                need_mini[pid] = list(range(n))
            else:
                missing = [i for i, pg in enumerate(pages) if pg is None]
                if len(pages) != n:
                    missing = list(range(n))
                if missing:
                    need_mini[pid] = missing
        need_est_pages = {}
        need_est_doc = []
        for pid in self._strip_ids:
            if presets.get(pid)["mode"] == "bw":
                counts = self._est_bytes.get((fkey, pid, dpi))
                if counts is None:
                    need_est_pages[pid] = list(range(n))
                else:
                    missing = [i for i, t in enumerate(counts) if t is None]
                    if len(counts) != n:
                        missing = list(range(n))
                    if missing:
                        need_est_pages[pid] = missing
            elif (fkey, pid) not in self._est_doc:
                need_est_doc.append(pid)
        need_preview = preview_key not in self._preview_cache
        if not need_mini and not need_est_pages and not need_est_doc and not need_preview:
            if self._job is not None:
                self._job_token.cancel()
                self._gen += 1
            self._reframe_minis()
            log.info("filter job skipped (cache hit) preset=%s", spec["preset_id"])
            return

        for pid in self._strip_ids:
            mt = len(need_mini.get(pid, ()))
            if presets.get(pid)["mode"] == "bw":
                et = len(need_est_pages.get(pid, ()))
            else:
                et = 0 if (fkey, pid) in self._est_doc else 1
            self._expect[pid] = [0, mt, 0, et]
            if mt == 0 and et == 0:
                self._filter_prog[pid] = 1.0
            else:
                self._filter_prog[pid] = 0.0
        self._reframe_minis()

        self._gen += 1
        self._job_token.cancel()
        self._job_token = CancelToken()
        filter_pool()  # warm on the main thread; workers only ever submit
        self.status.setText(f"Rendering filters… (job {self._gen})")
        log.info("filter job gen=%d pages=%d preset=%s workers<=%d need_mini=%d need_est=%d need_preview=%s",
                 self._gen, n, spec["preset_id"], cpu_cap(),
                 sum(len(v) for v in need_mini.values()),
                 sum(len(v) for v in need_est_pages.values()) + len(need_est_doc),
                 need_preview)
        job = FilterWorker(self.path, self._strip_ids, spec,
                           self._job_token, self._gen, n,
                           need_mini=need_mini, need_est_pages=need_est_pages,
                           need_est_doc=need_est_doc,
                           need_preview=need_preview)
        # Remember what this generation computes (stale gens never write).
        job._fkey = fkey
        job._est_dpi = dpi
        job._preview_key = preview_key
        job.mini_done.connect(self._jm_mini)
        job.est_done.connect(self._jm_est)
        job.preview_done.connect(self._jm_preview)
        job.progressed.connect(self._jm_progress)
        job.finished.connect(lambda: self._clear_job(job))
        self._job = job
        self._jobs.add(job)
        job.start()

    def _on_view_changed(self):
        """Any scroll/pan/zoom/layout change: reframe minis, debounced (§47)."""
        self._reframe_timer.start()

    def _current_view(self):
        """Framing both panes share: layout dims + visible scene rect."""
        cols = self.before.cols()
        pw = self.before._page_w()
        ph = self.before._page_h()
        vis = self.before.mapToScene(self.before.viewport().rect()).boundingRect()
        return cols, pw, ph, (vis.x(), vis.y(), vis.width(), vis.height())

    def _reframe_minis(self):
        """§48: repaint every mini as the current view through its own filter.

        Pure view work from cached per-preset pages — never a job, so this
        is what scroll/pan/zoom/page changes call (§47).
        """
        if not self.doc or not self.path:
            return
        for pid in self._strip_ids:
            self._reframe_one(pid)

    def _reframe_one(self, pid: str):
        if not self.doc or not self.path:
            return
        fkey = self._file_key()
        if fkey is None:
            return
        pages = self._mini_pages.get((fkey, pid))
        dpi = self.dpi.currentData()
        # §§55/59: real post-save amounts, no estimates anywhere. BW sums the
        # exact per-page payload bytes; color shows the exact per-image
        # decision total. Container overhead is reported at Save instead.
        if presets.get(pid)["mode"] == "bw":
            counts = self._est_bytes.get((fkey, pid, dpi))
            if counts is not None and len(counts) == self.doc.page_count and \
                    all(c is not None for c in counts):
                shown = fmt_bytes(sum(counts))
            else:
                shown = None
        else:
            total = self._est_doc.get((fkey, pid))
            shown = fmt_bytes(total) if total is not None else None
        if shown is not None:
            if self._mini_est.get(pid) != shown:
                self._mini_est[pid] = shown
        else:
            self._mini_est.pop(pid, None)
        if pages is not None and all(pg is not None for pg in pages):
            cols, pw, ph, vis = self._current_view()
            try:
                self._mini_view[pid] = frame_view(
                    pages, pw, ph, ContinuousDocView.GAP, cols, vis)
            except Exception:  # noqa: BLE001
                log.debug("reframe failed for %s", pid, exc_info=True)
                return
            exp = self._expect.get(pid)
            if exp is not None and (exp[1] or exp[3]):
                md, mt, ed, et = exp
                self._filter_prog[pid] = 0.5 * (md / mt if mt else 1.0) + \
                    0.5 * (ed / et if et else 1.0)
            else:
                self._filter_prog[pid] = 1.0
        self._paint_strip_item(pid)

    def _clear_job(self, job):
        self._jobs.discard(job)
        if self._job is job:
            self._job = None

    def _paint_strip_item(self, pid: str):
        if pid not in self._strip_ids:
            return
        prog = float(self._filter_prog.get(pid, 0.0))
        arr = self._mini_view.get(pid)
        if pid in self._mini_est:
            est = self._mini_est[pid]
        elif arr is not None:
            est = "sizing…"
        elif prog > 0.0:
            est = "working…"
        else:
            est = "queued…"
        icon = QPixmap(150, 190)
        icon.fill(Qt.white)
        pt = QPainter(icon)
        # §46: clear preview box — bordered frame around the mini, divided
        # from the small caption below it (§53: name, algorithm, size).
        box = (13, 2, 124, 112)
        pt.setPen(QPen(Qt.gray, 1))
        pt.drawRect(*box)
        if arr is not None:
            q = gray_to_qimage(arr) if arr.ndim == 2 else rgb_to_qimage(arr)
            mini = QPixmap.fromImage(q).scaled(120, 108, Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)
            pt.drawPixmap(box[0] + (box[2] - mini.width()) // 2,
                          box[1] + (box[3] - mini.height()) // 2, mini)
        else:
            small_ph = QFont(pt.font())
            small_ph.setPointSize(max(7, small_ph.pointSize() - 2))
            pt.setFont(small_ph)
            pt.drawText(box[0], box[1], box[2], box[3],
                        Qt.AlignCenter | Qt.TextWordWrap, "working…")
        # Divider between preview box and caption.
        pt.setPen(QPen(Qt.lightGray, 1))
        pt.drawLine(8, 120, 142, 120)
        small = QFont(pt.font())
        small.setPointSize(max(7, small.pointSize() - 2))
        pt.setFont(small)
        pt.setPen(QPen(Qt.black, 1))
        pt.drawText(0, 122, 150, 15, Qt.AlignHCenter, presets.get(pid)["label"])
        pt.setPen(QPen(Qt.darkGray, 1))
        pt.drawText(0, 137, 150, 14, Qt.AlignHCenter, _preset_algo(pid))
        pt.drawText(0, 151, 150, 14, Qt.AlignHCenter, est)
        if prog < 1.0:
            # §43: per-filter progress bar (status bar keeps only the aggregate).
            bx, by, bw, bh = 10, 170, 130, 8
            pt.fillRect(bx, by, bw, bh, Qt.lightGray)
            pt.fillRect(bx, by, int(round(bw * max(0.0, min(1.0, prog)))), bh, Qt.darkGreen)
        pt.end()
        self.filters.item(self._strip_ids.index(pid)).setIcon(QIcon(icon))
        self.filters.item(self._strip_ids.index(pid)).setText("")

    def _jm_mini(self, pid, page, arr, gen):
        if gen != self._gen:
            return
        job = self._job
        if job is None or getattr(job, "_fkey", None) != self._file_key():
            return
        n = self.doc.page_count if self.doc else 0
        key = (job._fkey, pid)
        pages = self._mini_pages.get(key)
        if pages is None or len(pages) != n:
            pages = [None] * n
            self._mini_pages[key] = pages
        if 0 <= page < n:
            pages[page] = arr
        exp = self._expect.get(pid)
        if exp is not None:
            exp[0] += 1
        self._reframe_one(pid)

    def _jm_est(self, pid, page, value, gen):
        if gen != self._gen:
            return
        job = self._job
        if job is None or getattr(job, "_fkey", None) != self._file_key():
            return
        if page < 0:
            # Whole-document color total (§59).
            self._est_doc[(job._fkey, pid)] = int(value)
        else:
            n = self.doc.page_count if self.doc else 0
            key = (job._fkey, pid, getattr(job, "_est_dpi", None))
            counts = self._est_bytes.get(key)
            if counts is None or len(counts) != n:
                counts = [None] * n
                self._est_bytes[key] = counts
            if 0 <= page < n:
                counts[page] = int(value)
        exp = self._expect.get(pid)
        if exp is not None:
            exp[2] += 1
        log.debug("job gen=%d %s p%s -> %dB", gen, pid, page + 1, value)
        self._reframe_one(pid)

    def _jm_preview(self, pages, gen):
        if gen != self._gen or not self.doc:
            return
        job = self._job
        pkey = getattr(job, "_preview_key", None)
        if pkey is not None:
            self._preview_cache[pkey] = list(pages)
            while len(self._preview_cache) > 2:  # bound memory: latest specs only
                self._preview_cache.pop(next(iter(self._preview_cache)))
        self._apply_preview_pages(pages, f"job {gen}")
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
        # §47: a page turn is a view change — reframe minis from cache only.
        self._reframe_minis()

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
        elif p["mode"] == "jpx":
            spec = {"mode": "jpx", "dpi_cap": p["params"]["dpi_cap"], "rate": p["params"].get("rate", 24)}
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
        # §53: the exact size is known once saving completes — report it with
        # the saving against the input.
        try:
            out_n = os.path.getsize(path)
            in_n = os.path.getsize(self.path) if self.path else 0
            delta = f" (was {fmt_bytes(in_n)}, −{100 * (1 - out_n / in_n):.0f}%)" \
                if in_n else ""
        except OSError:
            out_n, delta = -1, ""
        if out_n >= 0:
            log.info("saved %s — %s%s", path, fmt_bytes(out_n), delta)
            self.status.setText(f"Saved {os.path.basename(path)} — {fmt_bytes(out_n)}{delta}")
        else:
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
    log.info("starting pdf-minimalist debug=%s pdf=%s", debug, start_pdf)
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
