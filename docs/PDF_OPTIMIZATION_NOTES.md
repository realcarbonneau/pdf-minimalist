# PDF Optimization Notes (research + ideas)

## Correction: you mean JBIG2, not "JDIC2"
"JDIC2" doesn't exist — it's **JBIG2** (Joint Bi-level Image Experts Group,
ISO/IEC 14492). PDF natively supports it via `/Filter /JBIG2Decode`.
Remember as: **JBIG2 = black & white, JPEG2000 = color**.

## What PDF viewers actually support (verified Oct 2026)
PDF image filters in ISO 32000: `DCTDecode` (JPEG), `JPXDecode` (JPEG2000),
`JBIG2Decode`, `CCITTFaxDecode` (G3/G4), `FlateDecode`, `LZWDecode`, `RunLength`.
`pdfimages -list` shows these as `jpeg / jp2 / jbig2 / ccitt / image`.

**JPEG XL (JXL) is NOT embeddable in PDFs today.**
- JXL standardized 2022, great ratios (Cloudinary: ~40% smaller than PNG at same quality).
- Browsers: Safari ships it, Chrome 145 / Firefox 152 behind flags (2026).
- PDF Association announced Sep 2025 (PDF Days Europe) that JXL will be the
  *future* preferred format for HDR in PDF — no timeline, no spec update yet,
  no viewer support. Do NOT ship JXL-in-PDF in v0.1 or files won't open.
- Plan: offer JXL only as *sidecar export* (images extracted → `.jxl` folder
  alongside PDF), revisit embedding when ISO 32000 adds it.

## Codec cheat sheet
| Content | Best ratio | Universal fallback | Notes |
|---|---|---|---|
| 1-bit text/scan | JBIG2 lossless (jbig2enc), ~5–10x over G4 on books | CCITT G4 (built-in, fast) | Lossy JBIG2 (pattern matching, threshold ~0.8–0.85) saves extra 30–60% but can swap similar glyphs (e.g. `6`→`8`). Adobe/OCRmyPDF default threshold 0.85/0.82. US NARA rejects lossy JBIG2 for archives. |
| Gray/color photo | JPEG2000 (~20% smaller than JPEG) | JPEG q40–60, 4:2:0 | JP2 encode 5–10x slower, some viewers lag on 600dpi pages → auto-fallback to JPEG. ZIP/Flate only if lossless required. |
| Flat graphics | Flate + objstm + dedup | same | `garbage=4, deflate=1` already wins a lot. |

Real-world datapoint (jbig2-pdf-optimiser, book scans, threshold 0.8):
141× G4 pages 9.23MB → Acrobat JBIG2 1.77MB → global-dictionary JBIG2 1.46MB.
840 color JPG pages 951MB → BW JBIG2 30.5MB (−97%). BW wins big on text.

## BW threshold strategies (GIMP Threshold = "Simple")
1. **Simple / Global** (GIMP equivalent): `out = gray >= T ? 255 : 0`, T 0–255.
   Default T=127 (GIMP), but scans usually want 170–200. Fastest, predictable.
2. **Otsu** (auto global): picks T minimizing intra-class variance. No slider
   needed, best default. Needs numpy or OpenCV `cv2.threshold(..., THRESH_OTSU)`.
3. **Adaptive Mean / Gaussian**: per-pixel T from `blockSize×blockSize` neighborhood
   minus `C` (e.g. 31, C=10). Handles uneven light / shadows. Slower, can mottle
   backgrounds — add `median blur` prefilter option.
4. **Sauvola**: `T = mean * (1 + k*(std/R - 1))`, k≈0.2–0.34, R=128, window ~25–51px.
   Best for yellowed / stained paper, but slowest. Make opt-in under Balanced/Max.

Opinionated choice: dropdown `Simple | Otsu (default) | Adaptive | Sauvola`,
global slider always visible (disabled/auto-badge in Otsu unless overridden),
per-page table column `T override` (empty = use global).

## Ideas to try
- Pre-clean: autocontrast + light median (3px) before threshold reduces speckle.
- Despeckle post: drop connected components < N px (needs OpenCV or scipy).
- DPI ladder test: 200 vs 300 dpi BW — often 200dpi + JBIG2 beats 300dpi + G4.
- MRC (v0.3): split page into mask (JBIG2) + fg/bg (JPEG) like Acrobat
  "Adaptive Compression". 100:1 possible on magazines, but complex.
- Global JBIG2 dictionary across pages (like jbig2-pdf-optimiser, chunk 128 imgs)
  beats per-page dicts — wrap as `Effort=Max` option calling `jbig2enc -s` + replace.
- OCR sandwich (via OCRmyPDF/tesseract) to keep text searchable after rasterize.

## Tunables (Effort mapping)
- Max: 300dpi, Sauvola allowed, JBIG2 + global dict, JPEG q50 + try JP2, Brotli off (compat).
- Balanced: 250dpi, Otsu/adaptive, JBIG2 per-page else G4, JPEG q50.
- Fast: 200dpi, Otsu/simple, G4 only, JPEG q60, skip images <50KB.
