"""Per-page + whole-file BW pipeline with per-page cancel checks.

Defaults per designer brief: force full-page raster, 300 dpi, US Letter (8.5x11).
All three are overridable (main-screen options, per-preset, per-page).
"""
import fitz
import numpy as np
from PIL import Image
import io
from functools import wraps

from .cancel import CancelToken
from .pdf_io import CancelledError, render_gray, FITZ_LOCK
from . import threshold as T

# points (1/72 in). Letter = 8.5x11in, A4 = 210x297mm.
PAGE_SIZES = {
    "original": None,
    "letter": (612.0, 792.0),
    "a4": (595.28, 841.89),
}
DEFAULT_DPI = 300
DEFAULT_PAGE_SIZE = "letter"


def _fitz_locked(fn):
    """Serialize whole save jobs against preview workers (MuPDF aborts)."""
    @wraps(fn)
    def inner(*a, **k):
        with FITZ_LOCK:
            return fn(*a, **k)
    return inner


def bw_page_png(gray: np.ndarray, strategy: str = "otsu", t: int = 180) -> bytes:
    """Grayscale array -> 1-bit PNG bytes (G4-equivalent payload for preview)."""
    if strategy == "simple":
        bw = T.simple(gray, t)
    elif strategy == "otsu":
        bw = T.otsu(gray)
    elif strategy == "adaptive":
        bw = T.adaptive_mean(gray)
    elif strategy == "sauvola":
        bw = T.sauvola(gray)
    else:
        raise ValueError(strategy)
    img = Image.fromarray(bw).convert("1")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _fit_rect(src_w: float, src_h: float, dst_w: float, dst_h: float) -> fitz.Rect:
    """Aspect-fit src dimensions into dst page, centered."""
    scale = min(dst_w / src_w, dst_h / src_h)
    w, h = src_w * scale, src_h * scale
    x0 = (dst_w - w) / 2
    y0 = (dst_h - h) / 2
    return fitz.Rect(x0, y0, x0 + w, y0 + h)


@_fitz_locked
def process_file(in_path: str, out_path: str, strategy: str = "otsu", t: int = 180,
                 dpi: int = 300, token: CancelToken | None = None,
                 progress=None, per_page: dict | None = None,
                 page_size: str = DEFAULT_PAGE_SIZE, force_raster: bool = True):
    """Rasterize each page to 1-bit and rebuild PDF. Overwrites nothing in place.

    dpi: render resolution (default 300). page_size: "letter" | "a4" | "original".
    force_raster: True flattens every page to one image; False copies pages that
      carry extractable text through untouched (protects born-digital pages).
    per_page: {pageno: {"strategy"/"t"/"dpi"/"page_size"}} overrides.
    progress(pageno, total) called per page.
    Raises CancelledError on ESC. Deletes partial output on cancel (caller should unlink).
    """
    if page_size not in PAGE_SIZES:
        raise ValueError(f"page_size must be one of {sorted(PAGE_SIZES)}: {page_size!r}")
    token = token or CancelToken()
    per_page = per_page or {}
    src = fitz.open(in_path)
    out = fitz.open()
    try:
        for i in range(src.page_count):
            if token.cancelled:
                raise CancelledError()
            ov = per_page.get(i, {})
            strat = ov.get("strategy", strategy)
            tt = ov.get("t", t)
            dd = ov.get("dpi", dpi)
            ps = ov.get("page_size", page_size)
            if not force_raster and src[i].get_text().strip():
                out.insert_pdf(src, from_page=i, to_page=i)
                if progress:
                    progress(i + 1, src.page_count)
                continue
            gray = render_gray(src, i, dpi=dd, token=token)
            if token.cancelled:
                raise CancelledError()
            png = bw_page_png(gray, strat, tt)
            if token.cancelled:
                raise CancelledError()
            target = PAGE_SIZES[ps]
            if target is None:
                rect = src[i].rect
                page = out.new_page(width=rect.width, height=rect.height)
                page.insert_image(rect, stream=png)
            else:
                tw, th = target
                page = out.new_page(width=tw, height=th)
                srect = src[i].rect
                page.insert_image(_fit_rect(srect.width, srect.height, tw, th), stream=png)
            if progress:
                progress(i + 1, src.page_count)
        out.save(out_path, garbage=4, deflate=True, use_objstms=True)
    finally:
        out.close()
        src.close()


@_fitz_locked
def gc_copy(in_path: str, out_path: str):
    """Passthrough: garbage-collect + deflate, no pixel changes (Original preset)."""
    doc = fitz.open(in_path)
    try:
        doc.save(out_path, garbage=4, deflate=True, use_objstms=True)
    finally:
        doc.close()


@_fitz_locked
def recompress_file(in_path: str, out_path: str, dpi_cap: int = 150, jpeg_q: int = 50,
                    token: CancelToken | None = None, progress=None):
    """Color path: downsample oversized embedded images + re-encode JPEG.

    Only replaces a stream when the new bytes are strictly smaller. Skips
    1-bit images (BW path owns those), transparency masks, and images with
    alpha. Never rasterizes pages, so text/vectors survive.
    Raises CancelledError on ESC.
    """
    token = token or CancelToken()
    doc = fitz.open(in_path)
    done: set[int] = set()
    try:
        total = doc.page_count
        for pno in range(total):
            if token.cancelled:
                raise CancelledError()
            entries = doc[pno].get_images(full=True)
            masks = {e[1] for e in entries if e[1]}
            for e in entries:
                if token.cancelled:
                    raise CancelledError()
                xref = e[0]
                if xref in done or xref in masks:
                    continue
                done.add(xref)
                try:
                    info = doc.extract_image(xref)
                except Exception:
                    continue
                if info.get("bpc") == 1:
                    continue
                w, h = info["width"], info["height"]
                if max(w, h) < 200:
                    continue
                try:
                    img = Image.open(io.BytesIO(info["image"]))
                except Exception:
                    continue
                if img.mode in ("RGBA", "LA", "PA"):
                    continue
                img = img.convert("RGB")
                scale = min(1.0, (dpi_cap * 11) / max(w, h))
                if scale < 1.0:
                    img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, "JPEG", quality=jpeg_q, optimize=True)
                data = buf.getvalue()
                if len(data) >= len(info["image"]):
                    continue
                doc.update_stream(xref, data)
                doc.xref_set_key(xref, "Filter", "/DCTDecode")
                doc.xref_set_key(xref, "Width", str(img.width))
                doc.xref_set_key(xref, "Height", str(img.height))
                doc.xref_set_key(xref, "ColorSpace", "/DeviceRGB")
                doc.xref_set_key(xref, "BitsPerComponent", "8")
                try:
                    doc.xref_set_key(xref, "DecodeParms", "null")
                except Exception:
                    pass
            if progress:
                progress(pno + 1, total)
        doc.save(out_path, garbage=4, deflate=True, use_objstms=True)
    finally:
        doc.close()
