# Architecture & Tech Stack

## Decision (locked per designer rulings §6–§8, DROPPED D2): Python + PyMuPDF + Pillow + numpy, GUI = PySide6 (Qt6)

| Option | LXDE fit | Cross-platform | Preview speed | Verdict |
|---|---|---|---|---|
| PySide6 (Qt6) | good via apt or pip wheel | excellent DnD/HiDPI | best | **built — locked** |
| Tkinter (stdlib) + Pillow | excellent, zero extra GUI dep | good | OK but janky zoom | **superseded (D2)** — fails the designer's picky-UI standard |
| PyGObject GTK3 | most native on LXDE | painful on Win/Mac | good | rejected (portability) |
| Electron / Tauri | too heavy for old LXDE boxes | excellent | good | rejected |

Qt is built directly (`pdf_minimalist/ui_qt/`); there is no Tk code and no Tk-first
staging step. Pipeline code in `core/` must never import Qt.

## Dependencies (Debian 13)
```
sudo apt install python3-pymupdf python3-pil python3-numpy \
  python3-opencv  # optional, for Otsu/adaptive/Sauvola speed
  jbig2 poppler-utils  # optional: best BW encoder + pdfimages debug
pip install -r requirements.txt  # into local ./.venv (PySide6, pymupdf, Pillow, numpy)
```
- `PyMuPDF (fitz)` — open/render/replace images, `rewrite_images`, save with
  `garbage/deflate/use_objstms`. Version in trixie: 1.25.4 (good enough).
- `Pillow` — JPEG encode, 1-bit PNG/G4 payloads, numpy↔QImage preview bridge.
- `numpy` — threshold math without OpenCV. OpenCV used only if present.
- `jbig2enc` (external, `apt install jbig2enc` if available, else build) —
  only BW encoder PyMuPDF can't do alone. Fallback is G4 via Pillow/MuPDF.

## Module layout (actual)
```
pdf-minimalist/
  pdf_minimalist/
    core/             # headless, NO Qt imports
      cancel.py       # shared CancelToken (threading.Event + kill list)
      threshold.py    # simple / otsu / adaptive / sauvola, pure numpy
      pdf_io.py       # open, page count, gray render, save with gc
      pipeline.py     # BW full-page raster + color JPEG recompress + gc copy
      presets.py      # 8 opinionated presets, view modes, apply helpers
    ui_qt/            # Qt GUI only
      app.py          # DnD, pages, presets, main panes, save worker, ESC
      viewer.py       # QGraphicsView: wheel=scroll, ctrl+wheel=zoom, drag-pan, peer-synced
    __main__.py       # CLI: [pdf] [--debug]
  tests/  (see TEST_PLAN.md)
  tools/              # check_env, make_demo, shot (all scratch → .tmp/)
  docs/               # all analysis + rulings docs
```

## Threading & ESC cancel design
- One `QThread` Worker per save job; `CancelToken.event: threading.Event`.
  Pipeline checks `event.is_set()` after each page render, each image encode,
  each save step.
- Subprocesses launched via `Popen` stored in token; `cancel()` kills them.
- GUI: `<Escape>` bound at top level + Cancel button → `token.cancel()`.
  Worker polls, aborts, posts "Cancelled" status, deletes partial output.
- Preview renders also cancellable: debounce slider (150ms), kill stale render.
- Requirement: ESC → UI responsive again in <200ms, no zombie `jbig2enc`.

## Data flow (BW mode)
```
PDF page → fitz.get_pixmap(dpi=300) → numpy gray (0-255)
  → threshold(strategy, T) → 1-bit PIL image
  → encode G4 or JBIG2 → replace page with single image xref
  → save new PDF (garbage=4)
```
Color mode:
```
for each image xref: extract pix → downsample if >150dpi
  → re-encode JPEG q=X → replace only if smaller
→ save with gc + deflate
```

## Packaging
- v0.1: `python3 -m pdf_minimalist` from source + `requirements.txt`.
- Later: `.deb`, AppImage, `pipx`, Windows exe via PyInstaller (same `core/`).
