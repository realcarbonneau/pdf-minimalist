# Test Plan

## Automated (pytest, run with `python3 -m pytest`)
1. `test_threshold_simple`: 3×3 gray array, T=127 → exact 1-bit output.
2. `test_threshold_otsu`: synthetic bimodal image (half 50, half 200) → Otsu T in 100–150, output has both classes.
3. `test_threshold_adaptive`: gradient + dark corner → corner stays readable (no all-black).
4. `test_sauvola_stained`: yellowed-paper fixture → Sauvola keeps text, Simple@127 loses it (compare pixel counts).
5. `test_jpeg_smaller`: sample photo PDF image → q50 JPEG bytes < original PNG bytes.
6. `test_g4_roundtrip`: 1-bit image → G4 encode → decode → identical pixels.
7. `test_jbig2_if_present`: skip if no `jbig2` binary; else JBIG2 bytes < G4 bytes on text fixture.
8. `test_cancel`: 50-page fake job, set cancel after page 2 → pipeline aborts ≤5 pages, no output file left.
9. `test_esc_binding` (GUI smoke): root has `<Escape>` binding, Cancel button calls `token.cancel()`.
10. `test_no_overwrite`: save refuses to overwrite input path.

Fixtures to create in `tests/data/`:
- `scan_text_300dpi.png` (1 page, generated via PyMuPDF from text PDF)
- `yellowed_note.jpg` (photo of stained paper, or synthetic stains)
- `mixed_4pages.pdf` (text scan + photo + vector + blank)
- `born_digital_text.pdf` (selectable text, for warning test)

## Manual (LXDE Debian 13)
- [ ] DnD PDF from PCManFM onto app → opens. Button open works without tkdnd.
- [ ] Move threshold slider 0→255 → preview updates, extremes all-white/all-black.
- [ ] Per-page override page 3 to T=200, others global 170 → page 3 differs, rest same.
- [ ] Otsu on 10-page scan → readable, no hollow letters.
- [ ] Save BW: check size −60% or better on scans; open in Evince + MuPDF + Chromium.
- [ ] Save Color: JPEG q50 photo PDF −30% or better, no visible blocks at 100%.
- [ ] ESC during 20-page Max job → stops <1s, UI alive, partial file deleted.
- [ ] Kill `jbig2enc` path (rename binary) → app falls back to G4 with info bar, no crash.
- [ ] 1GB RAM limit (`systemd-run --scope -p MemoryMax=1G`) → 50-page PDF still completes (streaming, no OOM).
- [ ] No-network run (unplug) → everything works.

## Metrics to record per test
Input bytes, output bytes, % saved, time sec, effort preset, strategy, T, DPI,
encoder (G4/JBIG2/JPEG/JP2), viewer check (Evince OK?), readability 1–5.

## Definition of done (v0.1)
- BW scan book: −70% size, readable at 100%, ESC works, no overwrite, opens in 3 viewers.
