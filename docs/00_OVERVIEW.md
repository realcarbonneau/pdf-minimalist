# pdf-reducer — Overview & Opinionated Defaults

Target first: **LXDE on Debian 13 (trixie), Python 3.13**.
Goal later: same codebase runs on Windows / macOS / other Linux.

## What it does
Drag-and-drop (or File > Open) a PDF, visualize per-page and global size wins,
apply one of two opinionated pipelines, save a much smaller PDF.

Two pipelines only (v0.1):
1. **BW Document** — render page → grayscale → threshold → 1-bit → encode
   with JBIG2 (lossless default) / CCITT G4 fallback. For scans, notes, books.
2. **Color/Gray Recompress** — keep page as-is, extract embedded images,
   downsample + recompress to JPEG (default) or JPEG2000 (opt-in). For slides,
   photos in PDFs.

No magic "auto-optimize" button that silently destroys quality. Every action
shows before/after preview + bytes saved.

## Opinionated defaults (max compression first)
- DPI: render/threshold at 300 dpi, downsample color images to 150 dpi.
- BW threshold: **Otsu auto** global, manual slider 0–255 overrides global,
  per-page override table overrides global (GIMP Threshold equivalent = Simple mode).
- BW encode: **JBIG2 lossless** if `jbig2enc` present, else **CCITT G4**.
  Lossy JBIG2 OFF by default (character-substitution risk, NARA forbids lossy for archives).
- Color encode: **JPEG q=50, subsampling 4:2:0, optimize**, fallback to keep-original if larger.
  JPEG2000 OFF by default (20% smaller but 5–10x slower + viewer lag on big pages).
- PDF save: `garbage=4, deflate=1, use_objstms=1` (PyMuPDF), dedup images.
- Speed knob: single `Effort: Max | Balanced | Fast` that maps to the above.
  Max = smallest file, slowest. Fast = G4 + JPEG only, no JP2, no Sauvola.
- JPEG XL: **NOT used inside PDF in v0.1** (see `PDF_OPTIMIZATION_NOTES.md`).
  Optional sidecar export later.

## Non-negotiables
- **ESC cancels anything in <200ms.** Every long loop checks a cancel event
  per page, kills subprocesses (`jbig2enc`, `cjpeg`, etc.), cleans temp files.
- No network. No telemetry. Local files only.
- Never overwrite input. Output defaults to `<name>.reduced.pdf`.
- Born-digital PDFs (selectable text / vector) get a warning before BW rasterize,
  because BW mode in v0.1 destroys the text layer.

## v0.1 scope
- Open 1 PDF (DnD + button), page list with thumbnails, click page → large
  before/after preview, global threshold slider + strategy dropdown, per-page
  threshold override, size estimate label, Save + Cancel.
- No OCR, no MRC sandwich, no multi-file batch (v0.2).
