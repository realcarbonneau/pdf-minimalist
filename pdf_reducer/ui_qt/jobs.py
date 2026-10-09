"""Background filter rendering. The GUI thread never renders; it only views.

Concurrency (designer §37 + hard-won crash evidence):
- GUI-thread rendering froze the app (fixed by moving work out).
- A half-core ThreadPoolExecutor was tried next: bare `abort()` inside numpy
  in worker threads (not BLAS oversubscription, not MuPDF sharing — isolated
  numpy, isolated fitz and paired FilterWorkers all survive; only the full
  threaded path with Qt signals in play aborts).
- So: heavy compute runs in separate PROCESSES (spawn context, capped at half
  the cores — a real cap, real parallelism, crash-isolated: a worker crash
  becomes an error, never an app abort). The QThread here is only a manager:
  it submits, watches the cancel token between phases, and forwards results
  with the dispatch generation. Stale generations are never applied.
- Each process opens its OWN fitz handle; numpy/PIL never cross threads.
"""
import io
import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np
from PIL import Image as PILImage
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from ..core import presets
from ..core.pipeline import bw_page_png
from ..core.cancel import CancelToken

PREVIEW_DPI = 150
MINI_W = 160

_pool = None


def cpu_cap() -> int:
    """Max background worker processes: half the cores, at least 1."""
    return max(1, (os.cpu_count() or 2) // 2)


def pool():
    """Persistent spawn-context process pool (warmed on first dispatch).

    MUST be first created on the main thread (dispatch does this): spawning
    the pool's management threads/processes from a worker thread aborts.
    """
    global _pool
    if _pool is None:
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        _pool = ProcessPoolExecutor(max_workers=cpu_cap(),
                                    mp_context=mp.get_context("spawn"))
    return _pool


def shutdown_pool():
    global _pool
    if _pool is not None:
        _pool.shutdown(wait=False, cancel_futures=True)
        _pool = None


import atexit as _atexit
_atexit.register(shutdown_pool)


def _open(path):
    import fitz
    return fitz.open(path)


def render_gray(path: str, page: int, dpi: int) -> np.ndarray:
    import fitz
    from ..core.pdf_io import FITZ_LOCK
    with FITZ_LOCK:
        doc = _open(path)
        try:
            pix = doc[page].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
            return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()
        finally:
            doc.close()


def render_rgb(path: str, page: int, dpi: int) -> np.ndarray:
    import fitz
    from ..core.pdf_io import FITZ_LOCK
    with FITZ_LOCK:
        doc = _open(path)
        try:
            pix = doc[page].get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
            return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).copy()
        finally:
            doc.close()


def crop_view(gray: np.ndarray, crop) -> np.ndarray:
    """Crop (x, y, w, h) in render pixels, clamped, min 64px. None crop = whole."""
    if not crop:
        return gray
    h, w = gray.shape[:2]
    x, y, cw, ch = (int(v) for v in crop)
    x, y = max(0, x), max(0, y)
    cw, ch = max(64, min(cw, w - x)), max(64, min(ch, h - y))
    if x >= w or y >= h:
        return gray
    return gray[y:y + ch, x:x + cw]


def to_mini(arr: np.ndarray) -> np.ndarray:
    img = PILImage.fromarray(arr)
    img.thumbnail((MINI_W, 200), PILImage.LANCZOS)
    return np.asarray(img)


def mini_for_preset(gray_mini: np.ndarray, pid: str) -> np.ndarray:
    """Viewport mini for one preset (0/255 gray or RGB). Pure function."""
    p = presets.get(pid)
    if p["mode"] == "bw":
        from ..core import threshold as T
        s, t = p["params"]["strategy"], p["params"]["t"]
        fn = {"simple": lambda g: T.simple(g, t), "otsu": T.otsu,
              "adaptive": T.adaptive_mean, "sauvola": T.sauvola}[s]
        return fn(gray_mini)
    rgb = np.stack([gray_mini] * 3, axis=-1) if gray_mini.ndim == 2 else gray_mini
    return presets.apply_color_preview(rgb, pid)


def estimate_bytes(path: str, page: int, pid: str, dpi: int) -> int:
    """Real-encoder output size for one preset (own fitz handle; thread-safe)."""
    p = presets.get(pid)
    if p["mode"] == "bw":
        gray = render_gray(path, page, dpi)
        return len(bw_page_png(gray, p["params"]["strategy"], p["params"]["t"]))
    rgb = render_rgb(path, page, p["params"]["dpi_cap"])
    buf = io.BytesIO()
    PILImage.fromarray(rgb).save(buf, "JPEG", quality=p["params"]["jpeg_q"], optimize=True)
    return len(buf.getvalue())


def preview_page(path: str, page: int, spec: dict) -> np.ndarray:
    """Full preview render for one page under the active spec (own handle)."""
    from ..core import threshold as T
    if spec["mode"] == "color":
        rgb = render_rgb(path, page, PREVIEW_DPI)
        return presets.apply_color_preview(rgb, spec["preset_id"])
    if spec["mode"] == "passthrough":
        return render_rgb(path, page, PREVIEW_DPI)
    gray = render_gray(path, page, PREVIEW_DPI)
    s, t = spec["strategy"], spec["t"]
    fn = {"simple": lambda g: T.simple(g, t), "otsu": T.otsu,
          "adaptive": T.adaptive_mean, "sauvola": T.sauvola}[s]
    out = fn(gray)
    return np.stack([out] * 3, axis=-1)  # RGB for a uniform pane path


def mini_task(path: str, page: int, crop, pid: str) -> np.ndarray:
    """Viewport mini for one preset. Runs in a pool process (must stay picklable)."""
    gray = render_gray(path, page, PREVIEW_DPI)
    return mini_for_preset(to_mini(crop_view(gray, crop)), pid)


class FilterWorker(QThread):
    """One background job: viewport minis -> est. sizes -> full preview pages.

    Signals carry the dispatch generation; the GUI applies only the latest.
    """
    mini_done = Signal(str, object, int)   # pid, mini array, generation
    est_done = Signal(str, str, int)       # pid, "est. X", generation
    preview_done = Signal(object, int)     # [arrays...], generation
    progressed = Signal(int, int, int)     # done, total, generation

    def __init__(self, path, page, crop, preset_ids, spec, token, generation):
        super().__init__()
        self.path, self.page, self.crop = path, page, crop
        self.preset_ids = list(preset_ids)
        self.spec = dict(spec)
        self.token = token
        self.generation = generation

    @staticmethod
    def fmt(n: int) -> str:
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}MB"
        if n >= 1_000:
            return f"{n / 1_000:.0f}KB"
        return f"{n}B"

    def _alive(self):
        return not self.token.cancelled

    def run(self):
        self._run()

    def _run(self):
        import concurrent.futures as cf
        ex = pool()
        dpi = self.spec.get("dpi", 300)
        doc_n = self._page_count()
        if doc_n is None:
            return
        n_pages = doc_n
        # Phase 1 — viewport minis, one pool task per preset.
        if self._alive():
            futs = {ex.submit(mini_task, self.path, self.page, self.crop, pid): pid
                    for pid in self.preset_ids}
            for k, fut in enumerate(cf.as_completed(futs)):
                if not self._alive():
                    return
                pid = futs[fut]
                try:
                    self.mini_done.emit(pid, fut.result(), self.generation)
                except Exception:
                    pass
                self.progressed.emit(k + 1, len(self.preset_ids) * 2 + n_pages,
                                     self.generation)
        # Phase 2 — est. sizes, one pool task per preset.
        if self._alive():
            futs = {ex.submit(estimate_bytes, self.path, self.page, pid, dpi): pid
                    for pid in self.preset_ids}
            base = len(self.preset_ids)
            for k, fut in enumerate(cf.as_completed(futs)):
                if not self._alive():
                    return
                pid = futs[fut]
                try:
                    self.est_done.emit(pid, f"est. {self.fmt(fut.result())}", self.generation)
                except Exception:
                    pass
                self.progressed.emit(base + k + 1, base + len(self.preset_ids) + n_pages,
                                     self.generation)
        # Phase 3 — full preview pages for the active preset, pooled per page.
        if self._alive():
            futs = {ex.submit(preview_page, self.path, i, self.spec): i
                    for i in range(n_pages)}
            pages = {}
            for fut in cf.as_completed(futs):
                if not self._alive():
                    return
                try:
                    pages[futs[fut]] = fut.result()
                except Exception:
                    pass
                self.progressed.emit(len(self.preset_ids) * 2 + len(pages),
                                     len(self.preset_ids) * 2 + n_pages, self.generation)
            self.preview_done.emit([pages[i] for i in sorted(pages)], self.generation)

    def _page_count(self):
        import fitz
        from ..core.pdf_io import FITZ_LOCK
        try:
            with FITZ_LOCK:
                doc = fitz.open(self.path)
                try:
                    return doc.page_count
                finally:
                    doc.close()
        except Exception:
            return None
