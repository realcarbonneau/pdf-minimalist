"""Mandatory regression tests on hard scans (designer §36).

Faint handwriting, dark photocopies and ruled-paper scans must keep working:
thresholds may never silently blank a page or flood it to black.
"""
import glob
import os

import fitz  # noqa: E402
import numpy as np  # noqa: E402

from pdf_reducer.core import threshold as T  # noqa: E402
from pdf_reducer.core.pipeline import process_file  # noqa: E402
from pdf_reducer.core.cancel import CancelToken  # noqa: E402

SCANS = sorted(glob.glob("examples/scan-*.pdf"))
PAGES = {"scan-jfk-dark-letter.pdf": 6, "scan-jfk-ruled-list.pdf": 35,
         "scan-jfk-poor-copies.pdf": 8}


def _gray(pdf, page=0, dpi=150):
    d = fitz.open(pdf)
    pix = d[page].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()
    d.close()
    return arr


def _ink_frac(bw):
    return float((bw == 0).mean())


def test_scan_files_open_in_band():
    assert len(SCANS) >= 10, SCANS
    for f in SCANS:
        n = os.path.getsize(f)
        d = fitz.open(f)
        assert 200_000 <= n <= 50_000_000, (f, n)
        assert 3 <= d.page_count <= 50, (f, d.page_count)
        d.close()
    for f, n in PAGES.items():
        d = fitz.open(os.path.join("examples", f))
        assert d.page_count == n, (f, d.page_count)
        d.close()


def test_dark_letter_thresholds_keep_content():
    g = _gray("examples/scan-jfk-dark-letter.pdf", page=0)
    for name, out in [("otsu", T.otsu(g)), ("sauvola", T.sauvola(g)),
                      ("simple180", T.simple(g, 180))]:
        f = _ink_frac(out)
        assert 0.005 < f < 0.95, (name, f)  # neither blank nor flooded


def test_poor_copies_thresholds_keep_content():
    g = _gray("examples/scan-jfk-poor-copies.pdf", page=0)
    for name, out in [("otsu", T.otsu(g)), ("sauvola", T.sauvola(g))]:
        f = _ink_frac(out)
        assert 0.005 < f < 0.95, (name, f)


def test_bw_pipeline_roundtrips_scan(tmp_path):
    src = "examples/scan-jfk-surveillance-notes.pdf"
    out = str(tmp_path / "out.pdf")
    process_file(src, out, strategy="otsu", dpi=150, token=CancelToken())
    d = fitz.open(out)
    assert d.page_count == 9
    d.close()
