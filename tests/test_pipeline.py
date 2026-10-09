import fitz
import numpy as np
from PIL import Image
import io
from pdf_reducer.core.pipeline import process_file, recompress_file, gc_copy, PAGE_SIZES
from pdf_reducer.core.cancel import CancelToken


def _make_mixed(path: str):
    d = fitz.open()
    p = d.new_page(width=400, height=400)
    p.insert_text((50, 200), "Hello born-digital")
    d.save(path)
    d.close()


def test_letter_default(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    process_file(src, out, strategy="otsu", token=CancelToken())
    with fitz.open(out) as o:
        r = o[0].rect
        assert (round(r.width), round(r.height)) == (612, 792)


def test_original_size(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    process_file(src, out, strategy="otsu", page_size="original", token=CancelToken())
    with fitz.open(out) as o:
        r = o[0].rect
        assert (round(r.width), round(r.height)) == (400, 400)


def test_no_force_passthrough_keeps_text(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    process_file(src, out, strategy="otsu", force_raster=False, token=CancelToken())
    with fitz.open(out) as o:
        assert o[0].get_text().strip().startswith("Hello")


def test_bad_page_size_rejected(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    try:
        process_file(src, out, page_size="bogus", token=CancelToken())
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def _make_photo(path: str):
    rng = np.random.default_rng(7)
    arr = (rng.random((900, 1200, 3)) * 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    d = fitz.open()
    p = d.new_page(width=600, height=800)
    p.insert_image(fitz.Rect(0, 0, 600, 450), stream=buf.getvalue())
    p.insert_text((50, 700), "caption keeps text layer")
    d.save(path)
    d.close()


def test_color_recompress_shrinks_keeps_text(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_photo(src)
    n_in = len(open(src, "rb").read())
    recompress_file(src, out, dpi_cap=150, jpeg_q=45, token=CancelToken())
    n_out = len(open(out, "rb").read())
    assert n_out < n_in, (n_in, n_out)
    with fitz.open(out) as o:
        assert o.page_count == 1
        assert "caption" in o[0].get_text()


def test_gc_copy_roundtrip(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    gc_copy(src, out)
    with fitz.open(out) as o:
        assert o.page_count == 1
        assert "Hello" in o[0].get_text()
