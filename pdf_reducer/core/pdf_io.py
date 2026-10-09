"""PDF open/render/save helpers (PyMuPDF). Cancellable via CancelToken."""
import fitz  # PyMuPDF
import numpy as np
import threading

from .cancel import CancelToken

# MuPDF aborts under concurrent use from worker threads: serialize ALL fitz
# access process-wide through this re-entrant lock (renders are milliseconds;
# numpy/PIL encodes stay off-lock and overlap freely).
FITZ_LOCK = threading.RLock()


def open_doc(path: str) -> fitz.Document:
    return fitz.open(path)


def page_count(doc: fitz.Document) -> int:
    return doc.page_count


def render_gray(doc: fitz.Document, pageno: int, dpi: int = 200,
                token: CancelToken | None = None) -> np.ndarray:
    if token and token.cancelled:
        raise CancelledError()
    page = doc[pageno]
    with FITZ_LOCK:
        pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return arr.copy()


def save_doc(doc: fitz.Document, out_path: str):
    doc.save(out_path, garbage=4, deflate=True, use_objstms=True)


class CancelledError(RuntimeError):
    pass
