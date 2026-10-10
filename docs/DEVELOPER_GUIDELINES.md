# Developer guidelines — pdf-minimalist (full)

Read this before touching code. Source of truth for designer intent:
`DESIGNER_VERBATIM.md`. Request tracker: `../TODO.md` (repo root).
Root docs: `00_OVERVIEW.md`, `ARCHITECTURE.md`.
Entry points at repo root: `../README.md`, `../TODO.md`. All other analysis
docs live in this dir (`DESIGN.md`, `DROPPED.md`, `DESIGNER_VERBATIM.md`, …).

## 0. General guidelines (designer rulings — always in force)
- The designer is the sole authority. In all docs, call them "the designer".
- Designer words are preserved verbatim (see §1). Corrections and interpretations
  live OUTSIDE the quotes, never inside them.
- `TODO.md` tracks EVERY designer request: numbered append-only, NEVER renumbered
  or reordered. No checkboxes. Open items carry full detail; completed items are
  stubbed — request struck through, stub summary, cross-refs to the implementing
  docs/code. Dropped ideas move to `DROPPED.md` with reasons + revisit
  conditions. Knowledge is referenced, never redone.
- This file carries the designer's general rulings; `DESIGN.md` carries the
  design rulings with verbatim quotes. Both stay in sync with
  `DESIGNER_VERBATIM.md`.
- Docs lead: `docs/` is updated FIRST and carries decisions, rulings, and
  design intent; code and everything else follow. When docs and code disagree,
  fix the code to match the docs — or get a new designer ruling. Don't ask
  for direction the docs already give.

## 1. Keep designer comments verbatim — always
- NEVER fix the designer's spelling/grammar inside `DESIGNER_VERBATIM.md`.
  Typos (`targetting`, `remeber`, `lok`, `optmized`, `alll`, `alot`, double/triple spaces)
  are intentional preservation, not bugs.
- New designer note? Append it verbatim (full text, numbered, dated) before acting.
- Corrections (JDIC2→JBIG2, JXL dropped) go in the "Corrections log" section or in
  code/docs OUTSIDE the quotes — never by editing the quotes.

## 2. Stack & layout (locked unless the designer says otherwise)
- Python + PySide6 (Qt6) GUI + PyMuPDF pipeline. `core/` = headless, NO Qt imports.
  `ui_qt/` = widgets only. Pure-numpy thresholds (no hard OpenCV dep).
- REPOSITORY-OWNED: `pdf_minimalist/`, `tests/`, `tools/`, `docs/`,
  `requirements*.txt`, `.venv/` (git-ignored, via `setup_local.sh`).
- SYSTEM (apt, never vendored): `python3`, `jbig2`, `mutool`, `pdfimages`,
  Qt6 C++ libs. Never `sudo pip install`; pip targets `./.venv` only.

## 3. Opinionated product rules (from the brief)
- Max compression by default; single Effort knob (Max/Balanced/Fast) to trade speed.
- BW: Otsu auto default, Simple (= GIMP Threshold) + Adaptive + Sauvola available,
  global T slider + per-page override. Encode JBIG2 lossless (each page's
  stream is test-decoded before embedding; 1-bit PNG where the decoder
  can't take it).
  Lossy JBIG2 OFF by default (glyph-substitution risk).
- Color: downsample 150dpi + JPEG q~50 default; JPEG2000 opt-in only.
- NO JPEG XL inside PDFs (not in the spec, viewers can't open it).
- Never overwrite input; default `<name>.reduced.pdf`.
- Warn before rasterizing born-digital (selectable-text) PDFs in BW mode.

## 4. UX rules (the designer's picky-UI standard)
- Preset filter-strip (camera-filter UX) + main original/preview panes.
  View menu controls orientation of BOTH main panes and filter thumbnails
  (side-by-side H / stacked V). See `DESIGN.md`.
- Smooth `QGraphicsView`: wheel = scroll/pan, Ctrl+wheel = zoom-to-cursor, drag = pan, PgUp/PgDn = pages,
  fit-on-load, neighbor-page prefetch. No jank on old LXDE hardware.
- ESC cancels ANYTHING in <200ms: `CancelToken` checked per page/encode,
  subprocesses killed, partial output deleted, UI stays alive.
- PCManFM DnD (`text/uri-list`) + Open button fallback; 1024×600-friendly.

## 5. Workflow
- `./test.sh` (full `./.venv/bin/python -m pytest tests/ -q`) must stay green —
  designer ruling §59: run the FULL suite every time, before every ship.
- `python3 tools/check_env.py` then `./.venv/bin/python tools/check_env.py`.
- Qt smoke: `QT_QPA_PLATFORM=offscreen ./.venv/bin/python -c "...MainWindow..."`.
- Record per-test metrics (bytes in/out, % saved, secs, preset, viewer check).

## 6. Run-and-review logging (designer ruling — process, not UI/feature design)
- The app logs everything important to stdout: startup, open (path + page count),
  preset selection, preview renders (page/strategy/T/size), save params,
  job progress/completion, cancel requests, view-mode changes, warnings.
- `--debug` (`python -m pdf_minimalist --debug`) raises logging to DEBUG and dumps
  diagnostics: Python/PySide/Qt/fitz versions, cwd, argv, per-stage preview
  timings (render/threshold ms), per-page job progress.
- Default (no flag) stays INFO: quiet enough to run, complete enough to review
  what happened from the log alone.
