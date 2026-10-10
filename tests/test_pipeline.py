import fitz
import numpy as np
from PIL import Image
import io
from pdf_minimalist.core.pipeline import process_file, recompress_file, gc_copy, PAGE_SIZES
from pdf_minimalist.core.cancel import CancelToken


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


def _make_dense(path: str):
    import numpy as _np
    rng = _np.random.default_rng(11)
    arr = (rng.random((500, 400, 3)) * 255).astype(_np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    d = fitz.open()
    p = d.new_page(width=400, height=500)
    p.insert_image(fitz.Rect(0, 0, 400, 500), stream=buf.getvalue())
    d.save(path)
    d.close()


def test_jbig2_save_roundtrip(tmp_path):
    """Designer §3/§55: dense BW pages embed real JBIG2 and render with ink."""
    import shutil
    from pdf_minimalist.core.pipeline import bw_page_payload, jbig2_binary
    if shutil.which("jbig2") is None:
        import pytest
        pytest.skip("jbig2 binary missing")
    assert jbig2_binary() is not None
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_dense(src)
    process_file(src, out, strategy="otsu", dpi=100, token=CancelToken())
    with fitz.open(out) as o:
        assert o.page_count == 1
        imgs = o[0].get_images(full=True)
        assert imgs, "no embedded image"
        assert o.xref_get_key(imgs[0][0], "Filter")[1] == "/JBIG2Decode"
        px = o[0].get_pixmap(dpi=100, colorspace=fitz.csGRAY, alpha=False)
        got = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
        assert 0 in np.unique(got)  # ink survived, not a blank page
    # real payload beats the PNG fallback
    from pdf_minimalist.core.pdf_io import render_gray
    import fitz as _fz
    with _fz.open(src) as _d:
        g = render_gray(_d, 0, dpi=100, token=CancelToken())
    jb2, codec = bw_page_payload(g, "otsu")
    assert codec == "jbig2"
    from pdf_minimalist.core.pipeline import bw_page_png
    assert len(jb2) < len(bw_page_png(g, "otsu"))


def test_jbig2_fallback_stays_valid(tmp_path):
    """Sparse pages MuPDF cannot decode fall back to PNG — still valid ink."""
    import shutil
    if shutil.which("jbig2") is None:
        import pytest
        pytest.skip("jbig2 binary missing")
    from pdf_minimalist.core.pdf_io import render_gray
    import fitz as _fz
    from pdf_minimalist.core.pipeline import bw_page_payload
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    with _fz.open(src) as _d:
        g = render_gray(_d, 0, dpi=300, token=CancelToken())
    _jb2, codec = bw_page_payload(g, "otsu")
    assert codec == "png"  # this input's JBIG2 fails MuPDF decode
    process_file(src, out, strategy="otsu", token=CancelToken())
    with fitz.open(out) as o:
        px = o[0].get_pixmap(dpi=100, colorspace=fitz.csGRAY, alpha=False)
        got = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
        assert 0 in np.unique(got)  # ink, never a black-failure page


def test_jbig2_pixel_exact(tmp_path):
    """Dense JBIG2 embed round-trips bit-exact (lossless proof)."""
    import shutil
    if shutil.which("jbig2") is None:
        import pytest
        pytest.skip("jbig2 binary missing")
    from pdf_minimalist.core.pdf_io import render_gray
    from pdf_minimalist.core.pipeline import bw_page_jbig2, _place_bw, _threshold, jbig2_renders
    src = str(tmp_path / "in.pdf")
    _make_dense(src)
    with fitz.open(src) as _d:
        g = render_gray(_d, 0, dpi=100, token=CancelToken())
    h, w = g.shape
    jb2 = bw_page_jbig2(g, "otsu")
    assert jb2
    assert jbig2_renders(jb2, w, h, _threshold(g))
    out = fitz.open()
    s = 72 / 100
    page = out.new_page(width=w * s, height=h * s)
    _place_bw(out, page, fitz.Rect(0, 0, w * s, h * s), jb2, "jbig2", w, h)
    pdf = str(tmp_path / "t.pdf")
    out.save(pdf, garbage=4, deflate=True)
    out.close()
    with fitz.open(pdf) as o:
        px = o[0].get_pixmap(dpi=100, colorspace=fitz.csGRAY, alpha=False)
        got = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
    assert got.shape == _threshold(g).shape
    assert np.array_equal(got, _threshold(g))


def _make_flat_logo(path: str):
    """Few-color image (designer §57): flat red/blue/white, 3 colors."""
    import numpy as _np
    arr = _np.full((400, 500, 3), 255, dtype=_np.uint8)
    arr[50:200, 50:450] = (200, 30, 30)
    arr[220:350, 50:450] = (30, 60, 200)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    d = fitz.open()
    p = d.new_page(width=500, height=400)
    p.insert_image(fitz.Rect(0, 0, 500, 400), stream=buf.getvalue())
    d.save(path)
    d.close()


def test_jpx_recompress_roundtrip(tmp_path):
    """Designer §56: JPX codec path embeds JPXDecode and renders back."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_photo(src)
    before = len(open(src, "rb").read())
    recompress_file(src, out, dpi_cap=150, token=CancelToken(), codec="jpx", rate=24)
    after = len(open(out, "rb").read())
    assert after < before
    with fitz.open(out) as o:
        imgs = [e for p in o for e in p.get_images(full=True)]
        assert imgs, "no images left"
        assert "caption" in o[0].get_text()  # vectors/text preserved


def test_indexed_palette_wins_on_flat(tmp_path):
    """Designer §57: few-color images go lossless Flate, smaller than JPEG."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_flat_logo(src)
    recompress_file(src, out, dpi_cap=150, jpeg_q=45, token=CancelToken())
    with fitz.open(out) as o:
        imgs = o[0].get_images(full=True)
        assert imgs, "no embedded image"
        assert o.xref_get_key(imgs[0][0], "Filter")[1] == "/FlateDecode"
    assert len(open(out, "rb").read()) < len(open(src, "rb").read())
