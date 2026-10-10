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
MINI_PAGE_W = 200  # per-preset mini-page width (§48): framing-exact, not quality-led
MINI_PAGE_DPI = 72  # rendered small, then thumbnailed; the strip box is ~120px

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


def mini_page_task(path: str, page: int, pid: str) -> np.ndarray:
    """Small full-page render through one preset for mini compositing (§48).

    Runs in a pool process (must stay picklable). Always RGB so the
    framing composite has one code path; BW presets stack their 0/255 output.
    """
    p = presets.get(pid)
    if p["mode"] == "bw":
        from ..core import threshold as T
        gray = render_gray(path, page, MINI_PAGE_DPI)
        s, t = p["params"]["strategy"], p["params"]["t"]
        fn = {"simple": lambda g: T.simple(g, t), "otsu": T.otsu,
              "adaptive": T.adaptive_mean, "sauvola": T.sauvola}[s]
        out = fn(gray)
        rgb = np.stack([out] * 3, axis=-1)
    else:
        rgb = render_rgb(path, page, MINI_PAGE_DPI)
        rgb = presets.apply_color_preview(rgb, pid)
        rgb = np.asarray(rgb)
    img = PILImage.fromarray(rgb)
    w, h = img.size
    if w > MINI_PAGE_W:
        img = img.resize((MINI_PAGE_W, max(1, int(h * MINI_PAGE_W / w))), PILImage.LANCZOS)
    return np.asarray(img)


def frame_view(pages, pw: int, ph: int, gap: int, cols: int,
               visible, out_w: int = 150) -> np.ndarray:
    """Composite exactly the visible scene rect from per-preset mini-pages.

    Pure function (§48): `pages` are small RGB arrays (index-aligned, None for
    missing); `pw/ph` are the full-res base page dims the scene layout uses;
    `visible` is (x, y, w, h) in scene coords. Returns an RGB thumbnail that
    frames precisely what the main windows show — grid, gaps and cut-off last
    page included. Missing pages stay white.
    """
    vx, vy, vw, vh = (float(v) for v in visible)
    if vw <= 0 or vh <= 0:
        return np.full((8, 8, 3), 255, dtype=np.uint8)
    scale = out_w / vw
    cw, ch = max(1, int(round(vw * scale))), max(1, int(round(vh * scale)))
    canvas = np.full((ch, cw, 3), 255, dtype=np.uint8)
    n = len(pages)
    rows = (n + cols - 1) // cols if cols > 0 else 1
    for idx, pg in enumerate(pages):
        if pg is None:
            continue
        r, c = divmod(idx, max(1, cols))
        ix, iy = c * (pw + gap), r * (ph + gap)
        ox = max(ix, vx)
        oy = max(iy, vy)
        ox2 = min(ix + pw, vx + vw)
        oy2 = min(iy + ph, vy + vh)
        if ox2 <= ox or oy2 <= oy:
            continue
        H, W = pg.shape[:2]
        sx, sy = (W / pw) if pw else 1.0, (H / ph) if ph else 1.0
        px, py = int((ox - ix) * sx), int((oy - iy) * sy)
        px2, py2 = int(np.ceil((ox2 - ix) * sx)), int(np.ceil((oy2 - iy) * sy))
        px, py = max(0, px), max(0, py)
        px2, py2 = min(W, max(px + 1, px2)), min(H, max(py + 1, py2))
        if px2 <= px or py2 <= py:
            continue
        piece = pg[py:py2, px:px2]
        dx, dy = int(round((ox - vx) * scale)), int(round((oy - vy) * scale))
        dx2, dy2 = int(round((ox2 - vx) * scale)), int(round((oy2 - vy) * scale))
        dx, dy = max(0, dx), max(0, dy)
        dx2, dy2 = min(cw, max(dx + 1, dx2)), min(ch, max(dy + 1, dy2))
        if dx2 <= dx or dy2 <= dy:
            continue
        thumb = PILImage.fromarray(piece).resize((dx2 - dx, dy2 - dy), PILImage.LANCZOS)
        canvas[dy:dy2, dx:dx2] = np.asarray(thumb)
    _ = rows  # layout rows implied by page count; kept for clarity
    return canvas


class FilterWorker(QThread):
    """One background job: every preset × every page, once (§§37/44/48).

    Phase 1 — full preview pages for the active filter (§51: the right pane
    updates first). Phase 2 — mini-pages for exact-view compositing.
    Phase 3 — est. sizes. Scrolling, panning, zooming and
    page changes never dispatch: the GUI reframes minis from these caches.

    Signals carry the dispatch generation; the GUI applies only the latest.
    """
    mini_done = Signal(str, int, object, int)  # pid, page, mini-page array, generation
    est_done = Signal(str, int, int, int)      # pid, page, raw byte count, generation
    preview_done = Signal(object, int)     # [arrays...], generation
    progressed = Signal(int, int, int)     # done, total, generation

    def __init__(self, path, preset_ids, spec, token, generation, n_pages: int,
                   need_mini=None, need_est=None, need_preview=True):
        super().__init__()
        self.path = path
        self.preset_ids = list(preset_ids)
        self.spec = dict(spec)
        self.token = token
        self.generation = generation
        self.n_pages = int(n_pages)
        # §44 process-once: only compute what the GUI cache is missing.
        # need_mini/need_est map pid -> sorted list of missing page indices.
        self.need_mini = {pid: sorted(v) for pid, v in dict(need_mini or {}).items()}
        self.need_est = {pid: sorted(v) for pid, v in dict(need_est or {}).items()}
        self.need_preview = bool(need_preview)

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
        n_pages = self.n_pages
        mini_tasks = sum(len(v) for v in self.need_mini.values())
        est_tasks = sum(len(v) for v in self.need_est.values())
        total = mini_tasks + est_tasks + (n_pages if self.need_preview else 0)
        done = 0
        # Phase 1 — full preview pages for the ACTIVE filter first (§51): the
        # right pane is the designer's focus, so it updates before anything
        # else. Pooled per page.
        if self._alive() and self.need_preview:
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
                done += 1
                self.progressed.emit(done, total, self.generation)
            if len(pages) == n_pages:
                self.preview_done.emit([pages[i] for i in sorted(pages)], self.generation)
        # Phase 2 — mini-pages for exact-view compositing (§48).
        if self._alive() and mini_tasks:
            futs = {ex.submit(mini_page_task, self.path, i, pid): (pid, i)
                    for pid, idxs in self.need_mini.items() for i in idxs}
            for fut in cf.as_completed(futs):
                if not self._alive():
                    return
                pid, i = futs[fut]
                try:
                    self.mini_done.emit(pid, i, fut.result(), self.generation)
                except Exception:
                    pass
                done += 1
                self.progressed.emit(done, total, self.generation)
        # Phase 3 — est. sizes for every preset and page.
        if self._alive() and est_tasks:
            futs = {ex.submit(estimate_bytes, self.path, i, pid, dpi): (pid, i)
                    for pid, idxs in self.need_est.items() for i in idxs}
            for fut in cf.as_completed(futs):
                if not self._alive():
                    return
                pid, i = futs[fut]
                try:
                    self.est_done.emit(pid, i, int(fut.result()), self.generation)
                except Exception:
                    pass
                done += 1
                self.progressed.emit(done, total, self.generation)
