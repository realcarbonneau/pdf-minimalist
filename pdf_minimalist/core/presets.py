"""Opinionated preset list (camera-filter UX). Pure data + thin apply helpers.

No Qt imports here. UI renders thumbnails from apply_bw(); pipeline.py owns save.
"""
from . import threshold as T
from .pipeline import PAGE_SIZES, DEFAULT_DPI, DEFAULT_PAGE_SIZE, jpx_encode

RASTER_DPIS = (150, 200, 300, 600)
PAGE_SIZE_IDS = tuple(PAGE_SIZES)
PAGE_SIZE_LABELS = {
    "letter": "Letter 8.5×11",
    "a4": "A4",
    "original": "Original size",
}

PRESETS = [
    {"id": "orig", "label": "Original", "mode": "passthrough",
     "params": {}, "blurb": "gc+deflate only, baseline"},
    {"id": "bw-otsu", "label": "BW · Otsu Auto", "mode": "bw", "default": True,
     "params": {"strategy": "otsu", "t": 180, "dpi": 300, "encoder": "jbig2-g4"},
     "blurb": "best default for scans"},
    {"id": "bw-t180", "label": "BW · Clean T=180", "mode": "bw",
     "params": {"strategy": "simple", "t": 180, "dpi": 300, "encoder": "jbig2-g4"},
     "blurb": "clean laser prints (GIMP-Threshold style)"},
    {"id": "bw-t210", "label": "BW · Strong T=210", "mode": "bw",
     "params": {"strategy": "simple", "t": 210, "dpi": 300, "encoder": "jbig2-g4"},
     "blurb": "faint pencil / gray background"},
    {"id": "bw-sauvola", "label": "BW · Stained Paper", "mode": "bw",
     "params": {"strategy": "sauvola", "t": 180, "dpi": 300, "encoder": "jbig2-g4"},
     "blurb": "yellowed / uneven light, slower"},
    {"id": "bw-fast", "label": "BW · Fast Draft", "mode": "bw",
     "params": {"strategy": "otsu", "t": 180, "dpi": 200, "encoder": "g4"},
     "blurb": "quick pass on old hardware"},
    {"id": "color-j2k", "label": "Color · JPEG2000", "mode": "jpx",
     "params": {"dpi_cap": 150, "rate": 24},
     "blurb": "smallest photos, slower (default color)"},
    {"id": "color-max", "label": "Color · Max Squeeze", "mode": "color",
     "params": {"dpi_cap": 150, "jpeg_q": 45},
     "blurb": "smallest slides/photos"},
    {"id": "color-bal", "label": "Color · Balanced", "mode": "color",
     "params": {"dpi_cap": 200, "jpeg_q": 60},
     "blurb": "fewer JPEG blocks"},
]

VIEW_MAIN_MODES = ("side-h", "stack-v", "single")
VIEW_FILTER_MODES = ("film-h", "rail-v", "grid")


def get(preset_id: str) -> dict:
    for p in PRESETS:
        if p["id"] == preset_id:
            return p
    raise KeyError(preset_id)


def default_preset_id() -> str:
    for p in PRESETS:
        if p.get("default"):
            return p["id"]
    return "bw-otsu"


def apply_bw(gray, preset_id: str):
    """Grayscale numpy array -> 1-bit-ish (0/255) array for thumbnails/preview."""
    p = get(preset_id)
    if p["mode"] != "bw":
        raise ValueError(f"{preset_id} is not a BW preset")
    s = p["params"]["strategy"]
    t = p["params"]["t"]
    fn = {"simple": lambda g: T.simple(g, t), "otsu": T.otsu,
          "adaptive": T.adaptive_mean, "sauvola": T.sauvola}[s]
    return fn(gray)


def apply_color_preview(rgb, preset_id: str):
    """RGB numpy array -> JPEG-roundtripped preview at the preset's q/dpi_cap."""
    import numpy as np
    from PIL import Image
    import io
    p = get(preset_id)
    if p["mode"] != "color":
        raise ValueError(f"{preset_id} is not a color preset")
    q = p["params"]["jpeg_q"]
    cap = p["params"]["dpi_cap"]
    h, w = rgb.shape[:2]
    scale = min(1.0, (cap * 11) / max(w, h))
    img = Image.fromarray(rgb)
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=q, optimize=True)
    buf.seek(0)
    return np.asarray(Image.open(buf).convert("RGB"))


def apply_jpx_preview(rgb, preset_id: str):
    """RGB numpy array -> JPEG2000-roundtripped preview (designer §56)."""
    import numpy as np
    from PIL import Image
    import io
    p = get(preset_id)
    if p["mode"] != "jpx":
        raise ValueError(f"{preset_id} is not a JPEG2000 preset")
    data = jpx_encode(rgb, p["params"]["dpi_cap"], p["params"].get("rate", 24))
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGB"))
