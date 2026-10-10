"""Per-page + whole-file BW pipeline with per-page cancel checks.

Defaults per designer brief: force full-page raster, 300 dpi, US Letter (8.5x11).
All three are overridable (main-screen options, per-preset, per-page).
"""
import fitz
import numpy as np
from PIL import Image
import io
import logging
import os
import shutil
import subprocess
import tempfile
import zlib
from functools import wraps

from .cancel import CancelToken
from .pdf_io import CancelledError, render_gray, FITZ_LOCK
from . import threshold as T

log = logging.getLogger("pdf_minimalist")

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


def _threshold(gray: np.ndarray, strategy: str = "otsu", t: int = 180) -> np.ndarray:
    """Grayscale array -> 0/255 array (designer §3: the BW algorithm)."""
    if strategy == "simple":
        return T.simple(gray, t)
    elif strategy == "otsu":
        return T.otsu(gray)
    elif strategy == "adaptive":
        return T.adaptive_mean(gray)
    elif strategy == "sauvola":
        return T.sauvola(gray)
    else:
        raise ValueError(strategy)


def bw_page_png(gray: np.ndarray, strategy: str = "otsu", t: int = 180) -> bytes:
    """Grayscale array -> 1-bit PNG bytes (fallback payload when no JBIG2)."""
    bw = _threshold(gray, strategy, t)
    img = Image.fromarray(bw).convert("1")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def jbig2_binary() -> str | None:
    """Path to the JBIG2 encoder (designer §3), or None if not installed."""
    return shutil.which("jbig2")


def bw_page_jbig2(gray: np.ndarray, strategy: str = "otsu", t: int = 180,
                  timeout: int = 120) -> bytes | None:
    """Grayscale array -> self-contained JBIG2 page stream (designer §3).

    Lossless generic-region coding via `jbig2 -p` (PDF-ready data, no shared
    globals — every page decodes standalone). Returns None when the encoder
    is missing or fails; the caller falls back to 1-bit PNG.
    """
    if jbig2_binary() is None:
        return None
    bw = _threshold(gray, strategy, t)
    h, w = bw.shape[:2]
    fd, pbm = tempfile.mkstemp(suffix=".pbm")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(f"P4\n{w} {h}\n".encode())
            for row in (bw == 0):
                f.write(np.packbits(row).tobytes())
        try:
            r = subprocess.run(["jbig2", "-p", pbm], capture_output=True,
                               timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if r.returncode != 0 or not r.stdout:
            return None
        return bytes(r.stdout)
    finally:
        try:
            os.unlink(pbm)
        except OSError:
            pass


def bw_page_payload(gray: np.ndarray, strategy: str = "otsu", t: int = 180) -> tuple[bytes, str]:
    """Real save payload for one BW page: (bytes, "jbig2" | "png").

    JBIG2 wins only when the bytes test-decode pixel-exact in our own
    renderer: some small/sparse jbig2enc streams are valid JBIG2 (jbig2dec
    accepts them) yet MuPDF — the engine behind our previews and many
    viewers — cannot complete them and paints black. Shipping those would
    corrupt the document, so they fall back to 1-bit PNG. Estimator and saver
    share this function, so caption amounts always equal embedded bytes.
    """
    jb2 = bw_page_jbig2(gray, strategy, t)
    if jb2 is not None:
        bw = _threshold(gray, strategy, t)
        h, w = bw.shape[:2]
        if jbig2_renders(jb2, w, h, bw):
            return jb2, "jbig2"
    return bw_page_png(gray, strategy, t), "png"


def jbig2_renders(payload: bytes, w: int, h: int, expect: np.ndarray) -> bool:
    """True iff MuPDF decodes this JBIG2 stream back to `expect` (0/255).

    Same engine renders previews, main panes and minis: a stream that fails
    here must never be embedded.
    """
    try:
        d = fitz.open()
        try:
            page = d.new_page(width=w, height=h)
            _place_bw(d, page, fitz.Rect(0, 0, w, h), payload, "jbig2", w, h)
            px = page.get_pixmap(dpi=72, colorspace=fitz.csGRAY, alpha=False)
            got = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
            return got.shape == expect.shape and bool(np.array_equal(got, expect))
        finally:
            d.close()
    except Exception:
        return False


def _fit_rect(src_w: float, src_h: float, dst_w: float, dst_h: float) -> fitz.Rect:
    """Aspect-fit src dimensions into dst page, centered."""
    scale = min(dst_w / src_w, dst_h / src_h)
    w, h = src_w * scale, src_h * scale
    x0 = (dst_w - w) / 2
    y0 = (dst_h - h) / 2
    return fitz.Rect(x0, y0, x0 + w, y0 + h)


def jpx_encode(arr: np.ndarray, dpi_cap: int, rate: int = 24) -> bytes:
    """RGB array -> JPEG2000 bytes at the cap rule (designer §56).

    Shared by previews, estimates and saving so all three agree.
    """
    h, w = arr.shape[:2]
    scale = min(1.0, (dpi_cap * 11) / max(w, h))
    img = Image.fromarray(arr)
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG2000", quality_mode="rates", quality_layers=[rate])
    return buf.getvalue()


def flate_rgb_encode(arr: np.ndarray) -> bytes:
    """RGB array -> raw Flate stream bytes (filter byte 0 per row, zlib).

    Valid PDF FlateDecode payload, unlike PNG file bytes.
    """
    h = arr.shape[0]
    raw = b"".join(b"\x00" + np.ascontiguousarray(arr[y]).tobytes() for y in range(h))
    return zlib.compress(raw)


def indexed_flate_candidate(img: "Image.Image") -> bytes | None:
    """Few-color image (designer §57) -> lossless Flate RGB bytes, else None.

    Images with at most 256 distinct colors (logos, diagrams, flat UI shots)
    quantize to a 256-entry palette with zero visual change; re-expanded to
    RGB, they deflate to a fraction of a JPEG. Returns None when the image
    has more than 256 colors.
    """
    rgb = img.convert("RGB")
    if rgb.getcolors(maxcolors=257) is None:
        return None
    pal = rgb.quantize(colors=256, method=Image.MEDIANCUT).convert("RGB")
    return flate_rgb_encode(np.asarray(pal))


def color_stream_plan(image_bytes: bytes, w: int, h: int, bpc: int | None,
                      dpi_cap: int, jpeg_q: int = 45,
                      codec: str = "jpeg", rate: int = 24):
    """Decide one embedded image's fate: (replacement bytes, filter, W, H).

    Best tool wins per image (designer §57): the codec re-encode (baseline
    JPEG, or JPEG2000 when requested) plus, for images with at most 256
    distinct colors, a lossless palette-quantized Flate version. Returns None
    to keep the original stream (1-bit, tiny, alpha, undecodable, or nothing
    smaller). Saver and estimator share it, so captions equal saved bytes.
    """
    if bpc == 1:
        return None
    if max(w, h) < 200:
        return None
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return None
    if img.mode in ("RGBA", "LA", "PA"):
        return None
    img = img.convert("RGB")
    scale = min(1.0, (dpi_cap * 11) / max(w, h))
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    if codec == "jpx":
        buf = io.BytesIO()
        img.save(buf, "JPEG2000", quality_mode="rates", quality_layers=[rate])
        cands = [(buf.getvalue(), "/JPXDecode")]
    else:
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=jpeg_q, optimize=True)
        cands = [(buf.getvalue(), "/DCTDecode")]
    pal = indexed_flate_candidate(img)
    if pal is not None:
        cands.append((pal, "/FlateDecode"))
    data, filtr = min(cands, key=lambda c: len(c[0]))
    if len(data) >= len(image_bytes):
        return None
    return data, filtr, img.width, img.height


def _tiny_png() -> bytes:
    """1x1 1-bit placeholder: creates the image xref that a JBIG2 stream
    then replaces (`insert_image` rejects raw JBIG2, so the xref must first
    exist as a decodable image)."""
    img = Image.new("1", (1, 1), 1)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


_TINY = _tiny_png()


def _place_bw(out: "fitz.Document", page: "fitz.Page", rect: fitz.Rect,
              payload: bytes, codec: str, w: int, h: int):
    """Embed one BW page image: JBIG2Decode XObject, or plain PNG fallback."""
    if codec == "png":
        page.insert_image(rect, stream=payload)
        return
    page.insert_image(rect, stream=_TINY)
    imgs = page.get_images(full=True)
    if not imgs:
        raise ValueError("placeholder image xref missing")
    xref = imgs[-1][0]
    out.update_stream(xref, payload)
    out.xref_set_key(xref, "Filter", "/JBIG2Decode")
    out.xref_set_key(xref, "Width", str(w))
    out.xref_set_key(xref, "Height", str(h))
    out.xref_set_key(xref, "ColorSpace", "/DeviceGray")
    out.xref_set_key(xref, "BitsPerComponent", "1")
    for k in ("DecodeParms", "Interpolate"):
        try:
            out.xref_set_key(xref, k, "null")
        except Exception:
            pass


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
    n_jbig2 = n_png = 0
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
            payload, codec = bw_page_payload(gray, strat, tt)
            if codec == "jbig2":
                n_jbig2 += 1
            else:
                n_png += 1
                log.info("page %d: JBIG2 unusable here, PNG fallback", i + 1)
            if token.cancelled:
                raise CancelledError()
            target = PAGE_SIZES[ps]
            if target is None:
                rect = src[i].rect
                page = out.new_page(width=rect.width, height=rect.height)
                _place_bw(out, page, rect, payload, codec,
                          gray.shape[1], gray.shape[0])
            else:
                tw, th = target
                page = out.new_page(width=tw, height=th)
                srect = src[i].rect
                _place_bw(out, page,
                          _fit_rect(srect.width, srect.height, tw, th),
                          payload, codec, gray.shape[1], gray.shape[0])
            if progress:
                progress(i + 1, src.page_count)
        out.save(out_path, garbage=4, deflate=True, use_objstms=True)
        log.info("saved %s: BW pages JBIG2=%d PNG-fallback=%d", out_path, n_jbig2, n_png)
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
                    token: CancelToken | None = None, progress=None,
                    codec: str = "jpeg", rate: int = 24):
    """Color path: downsample oversized embedded images + re-encode.

    Designer §57: best tools win per image. Candidates per stream are the
    codec re-encode (JPEG baseline, or JPEG2000 when requested) plus, for
    images with at most 256 distinct colors, a lossless palette-quantized
    Flate version. Only a strictly smaller stream replaces the original.
    Skips 1-bit images (BW path owns those), transparency masks, and images
    with alpha. Never rasterizes pages, so text/vectors survive.
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
                plan = color_stream_plan(
                    info["image"], info["width"], info["height"],
                    info.get("bpc"), dpi_cap, jpeg_q, codec, rate)
                if plan is None:
                    continue
                data, filtr, nw, nh = plan
                doc.update_stream(xref, data)
                doc.xref_set_key(xref, "Filter", filtr)
                doc.xref_set_key(xref, "Width", str(nw))
                doc.xref_set_key(xref, "Height", str(nh))
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
