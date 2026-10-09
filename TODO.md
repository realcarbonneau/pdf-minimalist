# TODO — designer request log (append-only, NEVER renumber)

Format (designer ruling §16): no checkboxes. Open items carry full detail.
Completed items are stubbed: request struck through, stub summary, cross-refs
to the final docs/code that implement it. Dropped items move to
`docs/DROPPED.md` with reasons. Knowledge is referenced, never redone.
Mirrors `docs/DESIGNER_VERBATIM.md` § numbers.

## 1 — DONE
~~is my opencode harness up to date?  How do I update it?~~
Stub: version check + update instructions (Q&A, no artifact).

## 2 — DONE
~~`opencode update` fails: `Failed to change directory to .../update`.~~
Stub: explained — `update` isn't a command, parsed as project path; correct cmd is `opencode upgrade` (Q&A, no artifact).

## 3 — DONE
~~Full app-vision brief (scans → BW threshold + image recompression, max compression default, ESC cancel, md docs with notes/ideas/tests).~~
Stub: vision captured; 5 root analysis docs written.
See: `docs/00_OVERVIEW.md`, `docs/ARCHITECTURE.md`, `docs/PDF_OPTIMIZATION_NOTES.md`, `docs/UX_DESIGN.md`, `docs/TEST_PLAN.md`.

## 4 — DONE
~~Yes, JBIG2, summarize your suggestions to me.~~
Stub: confirmed JBIG2 (not JDIC2); suggestions summarized (Q&A + codec notes).
See: `docs/PDF_OPTIMIZATION_NOTES.md`.

## 5 — DONE
~~lok, no jxl. Rank frameworks by dependency size and OS/WM range.~~
Stub: JXL-in-PDF dropped; frameworks ranked smallest→largest with OS/WM coverage.
See: `docs/PDF_OPTIMIZATION_NOTES.md`, `docs/DROPPED.md` (D1).

## 6 — DONE
~~Picky smooth custom UI: pan, zoom in/out mouse scroll, next/prev page, DnD, etc.~~
Stub: ruled PySide6 + QGraphicsView (Tk Canvas too janky for the standard).
See: `docs/ARCHITECTURE.md`, `docs/UX_DESIGN.md`.

## 7 — DONE
~~Seems like Qt is really solid, can you double check?~~
Stub: verified 2026-10-09 — Qt 6.8.2 in trixie, PySide6 LGPL, QPdfView/QGraphicsView fit, LXDE/X11 OK.

## 8 — DONE
~~Start with Qt; everything local in this directory; tell me what is local vs system packages.~~
Stub: local scaffold built; local-vs-system split documented.
See: `pdf_reducer/`, `.venv/`, `requirements*.txt`, `setup_local.sh`, `docs/DEPENDENCIES.md`, `README.md`.

## 9 — DONE
~~Verbatim comments in a design doc, docs dir, dev guidance doc, preset list like camera photo filters with small previews, click → main original+preview side by side H/V, same for filter thumbnails, all as menu view options.~~
Stub: docs dir + verbatim file + dev guidance + 8-preset strip + View menu (main H/V/single, filters film/rail/grid) built and smoke-tested.
See: `docs/DESIGNER_VERBATIM.md`, `docs/DEVELOPER_GUIDELINES.md`, `docs/DESIGN.md`, `pdf_reducer/core/presets.py`, `pdf_reducer/ui_qt/app.py`.
Open follow-up (offered, awaiting designer ruling): live-rendered 96px thumbnail minis in the strip (currently label rows).

## 10 — DONE
~~Generally forcing alll images on the page and page rasterizing to 300dpi, and 8.5x11, but that also would be options on the main screen.~~
Stub: force-raster + 300dpi + Letter defaults, all three as main-screen controls (DPI combo, page-size combo, force checkbox); force-off passes text pages through.
See: `pdf_reducer/core/pipeline.py`, `pdf_reducer/core/presets.py`, `pdf_reducer/ui_qt/app.py`, `tests/test_pipeline.py`.

## 11 — DONE
~~In the docs, always call the operator/user the designer.~~
Stub: docs prose normalized to "the designer"; verbatim quotes untouched.
See: `docs/DESIGN.md` (rulings section), `docs/DEVELOPER_GUIDELINES.md`, `docs/DESIGNER_VERBATIM.md`.

## 12 — DONE
~~Finish prior work + every request in TODO.md, numbered, never renumbered.~~
Stub: this log exists; prior work finished per item.
See: `TODO.md`.

## 13 — DONE
~~Dev guidance carries general-guideline rulings incl. TODO instructions.~~
Stub: general rulings live in dev guidance.
See: `docs/DEVELOPER_GUIDELINES.md` (§0).

## 14 — DONE
~~Run the UI so I can see; log everything important to stdout for run-and-review; --debug dumps more; belongs in dev guidelines (process, not UI/feature).~~
Stub: INFO stdout logging everywhere, `--debug` adds versions/argv/timings, `./run.sh` launcher + `.tmp/` log, offscreen review shots.
See: `pdf_reducer/ui_qt/app.py` (`setup_logging`), `pdf_reducer/__main__.py`, `docs/DEVELOPER_GUIDELINES.md` (§6), `run.sh`, `tools/shot.py`.

## 15 — DONE
~~Stay inside the local dir; scratch in gitignored ./.tmp/; GitHub-ready later.~~
Stub: all scratch local; repo clean for future push.
See: `.tmp/`, `.gitignore`, `run.sh`, `tools/make_demo.py`, `tools/shot.py`.

## 16 — DONE
~~TODO format ruling + dropped-ideas doc (verbatim §16).~~
Stub: this file's format + dropped log established.
See: `TODO.md` (this file), `docs/DROPPED.md`, `docs/DEVELOPER_GUIDELINES.md` (§0).

## 17 — DONE
~~call it the full developper guidlines md doc~~
Stub: dev guidance renamed to its full name.
See: `docs/DEVELOPER_GUIDELINES.md`.

## 18 — DONE
~~move most of your docs to the docs dir please~~
Stub: analysis docs moved to `docs/`; `README.md` + `TODO.md` stay at root; all xrefs fixed.
See: `docs/`, `README.md`.

## 19 — DONE
~~docs-lead ruling (verbatim §19).~~
Stub: all doc xrefs corrected first, ruling recorded, then verification.
See: `docs/DEVELOPER_GUIDELINES.md` (§0).

## 20 — DONE
~~continue, why did you stop?~~
Stub: ARCHITECTURE fixed to Qt-locked (D2); Save now dispatches by preset
mode — BW raster, color JPEG recompress, gc passthrough — with previews.
See: `docs/ARCHITECTURE.md`, `pdf_reducer/core/pipeline.py`
(`recompress_file`, `gc_copy`), `pdf_reducer/core/presets.py`
(`apply_color_preview`), `pdf_reducer/ui_qt/app.py`, `tests/test_pipeline.py`.
Remaining queue (not yet ruled on): JBIG2 wiring, GitHub push.

## 21 — DONE
~~run the app, or it's not reaady?~~
Stub: READY and RUNNING — live on the designer display (pid confirmed, window
shown, log streaming to `.tmp/pdf-reducer.log`, live screenshot in `.tmp/`).
Earlier failure was my sandbox's `pkill -f` matching its own command line;
relaunch used a self-safe pattern. Leave it running for designer review;
`./run.sh` relaunches any time.
See: `run.sh`, `.tmp/pdf-reducer.log`, `.tmp/shot-live.png`.

## 22 — DONE
~~page zoom, pan, etc is always synced on both panes~~
Stub: original/preview panes mirror zoom + pan/scroll both ways (peer sync
with reentrancy guard); covered by sync test.
See: `docs/DESIGN.md` (Behavior), `pdf_reducer/ui_qt/viewer.py`,
`tests/test_viewer_sync.py`.

## 23 — DONE
~~left side is baseline, so no preview of basline, right side is per filter.~~
Stub: left pane fixed baseline; right pane shows selected filter; strip renders
a live mini per filter of the current page (icon mode, preset params).
See: `docs/DESIGN.md` (Behavior), `pdf_reducer/ui_qt/app.py`
(`_render_filter_minis`), `tests/test_minis.py`, `.tmp/shot-main.png`.

## 24 — DONE
~~find a few public pdf docs that are representative test cases, not too big, 1
to 10 pages, 200k to 10 mb, put in examples dir in this repo~~
Stub: 4 pdf.js-corpus PDFs committed (photo/mixed/vector/vector-stress) +
`examples/README.md` with profiles + spot metrics.
See: `examples/`, `examples/README.md`.

## 25 — DONE
~~also ctl mouse scroll is up/down? Or mouse scroll is page scroll and ctl wheel
is zoom, I think that is more common ui, no?~~
Stub: common convention adopted — plain wheel scrolls, Ctrl+wheel zooms,
both panes stay synced. Covered by wheel test.
See: `pdf_reducer/ui_qt/viewer.py`, `tests/test_viewer_sync.py`,
`docs/DEVELOPER_GUIDELINES.md`, `docs/ARCHITECTURE.md`.

## 26 — DONE
~~the page viewer should be continuous by default, with a gap between paged.
No page list to the left. Zoom out should aso autowrap to multiple pages per
side if it fits in the window width.~~
Stub: both panes are continuous scrollers (24px gap, autowrap grid by
viewport/zoom, synced zoom+scroll); page list removed, status shows Page N of
M; PgUp/PgDn jump pages; minis follow the top-visible page.
See: `docs/DESIGN.md` (Behavior), `pdf_reducer/ui_qt/viewer.py`
(`ContinuousDocView`), `pdf_reducer/ui_qt/app.py`, `tests/test_continuous.py`,
`.tmp/shot-main.png`.

## 27 — DONE
~~Did you find example pdfs? Your pdf file is not a good example at all.~~
Stub: yes — 4 real PDFs were already in `examples/` (item 24); the synthetic
`.tmp/demo.pdf` is retired from demos. Live app + screenshots switched to
`examples/images.pdf` (photo-heavy); window confirmed on the designer display.
See: `examples/`, `examples/README.md`.

## 28 — DONE
~~use a 3 page example for the tests please.~~
Stub: `examples/filled-background.pdf` (3 pages, 401KB, pdf.js corpus) —
probed ~30 corpus files, only 3-pager in the 200KB–10MB band; exercises
continuous scroll, page jumps, and multi-page render.
See: `examples/`, `examples/README.md`.

## 29 — OPEN (full detail, partial progress)
Designer: only 5 examples; want real-world types — deeds, research papers,
documentations, appliance manuals, etc. Landed: recorded deed
(`deed-brevard.pdf`, scan-like), appliance quick-start
(`manual-maytag-dryer.pdf`), government form (`form-fw9.pdf`), research paper
(`paper-arxiv-1406.2661.pdf`) — 9 examples total. Still open: software/project
documentation. (Two requested-type files sit under the 200KB floor — noted in
`examples/README.md`.)

## 30 — DONE
~~Also, why is original still in the filters? Or did you not relaunch the
latest version?~~
Stub: it was code, not a stale launch (relaunches verified by pid + log).
Strip now shows only the 7 real filters (passthrough excluded — left pane is
the baseline); preset combo keeps all 8 modes for Save; strip↔preset mapping
is by id. Covered by strip-sync test; live instance relaunched on the build.
See: `pdf_reducer/ui_qt/app.py`, `tests/test_minis.py`, `docs/DESIGN.md`.

## 31 — DONE
~~why are you using that terrible pdf as a default?~~
Stub: default demo is now `examples/images.pdf` (photo-heavy); `run.sh` with
no args opens it; `tools/shot.py` default updated too. `filled-background.pdf`
kept only as the 3-page scroll test.
See: `run.sh`, `tools/shot.py`.

## 32 — DONE
~~the app should show the final size of each filter below it. It should also
show the small preview which is mirroring the current view on the original.
Remove the left panel and put the options in the menu or in the right panel,
there will only be one tool panel and a menu.~~
Stub: strip minis carry real encoder-based est. sizes; OverviewMap navigator
(baseline page + viewport rect, click/drag to jump); left panel deleted —
File menu (Open/Save/Quit), single right panel, page/progress/status in the
status bar.
See: `docs/DESIGN.md` (Behavior), `pdf_reducer/ui_qt/app.py`,
`pdf_reducer/ui_qt/overview.py`, `pdf_reducer/ui_qt/viewer.py`,
`tests/test_minis.py`, `tests/test_continuous.py`, `.tmp/shot-main.png`.

## 33 — DONE
~~Don't show the tooltips at the top, waste of space, we will find another
place for that~~
Stub: pane/strip header labels removed; hints live as zero-space hover
tooltips pending final placement.
See: `pdf_reducer/ui_qt/app.py`.

## 34 — DONE
~~For now, fit everything you can on the right side panel or in the menu.~~
Stub: done as part of item 32 (File menu + single right panel + status bar).
See: `pdf_reducer/ui_qt/app.py`.

## 35 — DONE
~~document, compile and collect these, document in an examples md doc with
descriptions, view them also. [corpus brief]~~
Stub: `tools/corpus/` (27-record manifest.json + fetch_and_validate.py →
corpus_report.csv OK/OUT_OF_RANGE/ERROR); 26/27 fetched (CDC stacks 403s
scripts — noted); committed to `examples/` (~127MB, 35 files); full table +
codecs + spot metrics in `examples/README.md`; contact sheet viewed.
New band recorded: 3–50p / 200KB–50MB supersedes §24 for additions.
See: `tools/corpus/`, `examples/`, `examples/README.md`, `.tmp/contact.png`.

## 36 — DONE
~~[historical scan set brief]~~
Stub: 10 scans fetched (NACA ×4, NARA schedule, JFK ×5); LoC leads logged
manual in README (no direct PDFs). Faint/dark/ruled scans are now mandatory
regression tests — thresholds must never blank or flood a page.
See: `examples/scan-*.pdf`, `tests/test_regression_scans.py`.
Remaining queue (not yet ruled on): JBIG2 wiring, GitHub push, software
documentation example.

## 37 — DONE
~~don't freeze the whole app when doing the previews, do it in background [...]
(full §37 in verbatim)~~
Stub: FilterWorker (QThread manager) runs minis→estimates→preview in separate
spawn-context PROCESSES capped at half the cores (real cap, crash-isolated),
results applied by generation; minis mirror the viewport; pan/zoom is pure
view; progress per filter + status bar. Hardened along the way: never drop the
last ref of a running QThread (Qt fatal — track in-flight workers); preview
application suppresses sync cascades and preserves scroll/zoom; splitter
stretch keeps panes equal. Sort-filters/max-auto deferred.
See: `pdf_reducer/ui_qt/jobs.py`, `docs/DESIGN.md`.

## 38 — OPEN (full detail)
Designer audit: consolidate to ~22–23 (reserve: Kepler, Swift, 2 JFK, TM972,
formulas + others), add camera-photo PDFs (DocShadow subset, SmartDoc),
DIBCO quantitative tests, structural classes (PDF/A, JBIG2-done, OCR text),
processing ladder, automatic "B&W not recommended" recommendation.

## 39 — DONE
~~I called my github repo, pdf-minimalist, I should already have ssh to github
working locally, can you migrate and sync to github? There is only a
placeholder readme there, everything can be replaced, but double check to make
sure you have the correct repo.~~
Stub: verified SSH as realcarbonneau + remote (one commit, single "# pdf-squash"
stub) before touching anything; `git init/add/commit`, 81 files, pushed with
--force replacing the stub (authorized). Working tree clean, tracking
origin/main. Note: local package still named pdf_reducer (no rename ruled).
See: https://github.com/realcarbonneau/pdf-minimalist (commit 78544a0).
Remaining queue (not yet ruled on): JBIG2 wiring, software
documentation example.
