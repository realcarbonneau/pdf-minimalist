from pdf_minimalist.core import presets


def test_preset_ids_unique():
    ids = [p["id"] for p in presets.PRESETS]
    assert len(ids) == len(set(ids))


def test_default_is_bw():
    p = presets.get(presets.default_preset_id())
    assert p["mode"] == "bw"


def test_view_modes_known():
    assert set(presets.VIEW_MAIN_MODES) == {"side-h", "stack-v", "single"}
    assert set(presets.VIEW_FILTER_MODES) == {"film-h", "rail-v", "grid"}


def test_apply_bw_shapes():
    import numpy as np
    gray = np.full((8, 8), 128, dtype=np.uint8)
    gray[:, 4:] = 200
    for pid in ["bw-otsu", "bw-t180", "bw-t210", "bw-sauvola", "bw-fast"]:
        out = presets.apply_bw(gray, pid)
        assert out.shape == gray.shape
        assert set(np.unique(out).tolist()) <= {0, 255}
