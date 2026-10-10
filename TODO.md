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

## 40 — DONE
~~change the various names and stubs that has pdf-reducer, to
pdf-minimalist.~~
Stub: `git mv pdf_reducer/ pdf_minimalist/` + all `from pdf_reducer`
imports → `pdf_minimalist` (8 test files); display strings/docs already
renamed; `run.sh` + `tools/shot.py` now resolve; `python -m pdf_minimalist`
verified; 27/27 tests green. Historical `TODO.md` stubs keep old paths.
See: `pdf_minimalist/`, `tests/`, `run.sh`, `tools/shot.py`.

## 41 — DONE
~~also, why does it say local? Ref: pdf-reducer (local)~~
Stub: title → `pdf-minimalist`, `LOCAL` → repository-owned; part of the
item-40 rename, verified in `README.md` / `DEPENDENCIES.md` /
`DEVELOPER_GUIDELINES.md`.
See: `README.md`, `docs/DEPENDENCIES.md`, `docs/DEVELOPER_GUIDELINES.md`.

## 42 — DONE
~~push everything together, it doesn't matter for now, this is just a
startup.~~
Stub: single startup commit `0a9eeaf` pushed to `origin/main`
(https://github.com/realcarbonneau/pdf-minimalist) covering the rename plus
items 40–41 and 43–54; working tree clean and tracking. Item 39's remote
check still stands.

## 43 — DONE
~~the progress bar is supposed to be for EACH filter.~~
Stub: each strip mini now paints its own bar (`working…` 0.0 → mini 0.5 →
`est. X` 1.0, bar hidden when done); status bar keeps only the aggregate.
Verified by offscreen run (all 7 reach 1.0, icons non-null).
See: `docs/DESIGN.md` (Behavior), `pdf_minimalist/ui_qt/app.py`
(`_paint_strip_item`, `_filter_prog`), `pdf_minimalist/ui_qt/jobs.py`.

## 44 — DONE
~~when I was clicking on a filter preview, it seemed to be restarting it
processing, but that is incorrect, it should be processed once and only
reprocessed if there is a change of the file or change in the filter
specifications.~~
Stub: process-once cache — file identity (path+mtime+size) + top page +
spec tuple (preset/mode/dpi/strategy/t); strip/preset clicks hit
`_try_apply_cached` with no new job; `FilterWorker` takes
`need_mini/need_est/need_preview` so partial misses only compute what's
missing. Verified: cache-hit dispatch bumps no gen, same-row click no job,
spec change reprocesses + grows cache 1→2; 27/27 tests green.
See: `docs/DESIGN.md` (Behavior), `pdf_minimalist/ui_qt/app.py`
(`_file_key`, `_dispatch_filters`, `_try_apply_cached`, `_preview_cache`),
`pdf_minimalist/ui_qt/jobs.py`.

## 45 — DONE (superseded by 48)
~~Previews are truncated half page or something, when they should should the
exact preview seen in the preview window.~~
Stub: interim fix rendered minis full-page (killed the top-slice truncation,
verified offscreen). Designer §48 then clarified the ruling: minis must mirror
the main view's exact framing (multi-page grid included), each from its own
filter's preprocessed file — implemented under item 48.
See: `docs/DESIGN.md` (Behavior), item 48.

## 46 — DONE
~~Also, make the thumbnail preview box clear and the filter and size below it
in smaller characters and aso clearly divided~~
Stub: bordered preview frame + divider line + small caption (name dark, est
gray) painted per mini; verified offscreen (`shot-main.png`).
See: `pdf_minimalist/ui_qt/app.py` (`_paint_strip_item`).

## 47 — DONE
~~again, why is there reprocessing when I scroll????~~
Stub: scroll/pan/zoom/page turns are pure view now — never a job. Cause was
the single-page mini/est cache wiped on every top-page change; fixed by the
item-48 redesign (per-preset full-document caches + reframe). Verified
offscreen on a 6-page doc: page turn and scrollbar moves bump no generation,
no job object.
See: `pdf_minimalist/ui_qt/app.py` (`_reframe_minis`, `_on_page_changed`).

## 48 — DONE
~~Still wrong! Thumbnails should be a mini version of exactly the current view
of the larger window. [...] each preview shows exactly that from it's own
filter view (internal, no shown, file preprocessed in bg at the start or from
the latest change).~~
Stub: every preset × every page preprocessed once in background (mini-pages
~200px + est sizes for all pages; 150dpi preview pages for the active spec);
each mini composites exactly the synced main-view framing from its own
preset's pages (`frame_view`); reframe on scroll with zero jobs; new jobs
only on file/spec change; preview cache capped at 2 specs. Verified: 27/27
tests green + offscreen 6-page check (framing aspect == main view, click
dispatches exactly one preview-only job, click-back cached).
See: `docs/DESIGN.md` (Behavior), `pdf_minimalist/ui_qt/jobs.py`
(`mini_page_task`, `frame_view`, `FilterWorker`),
`pdf_minimalist/ui_qt/app.py` (stores, `_reframe_minis`, `_dispatch_filters`).

## 59 — DONE
~~please complete your work, don't stop half compelted.  Also make a full test
suite please and run each time please.~~
Stub: finished in flight — color captions are real post-save amounts (saver
and estimator share `color_stream_plan` with doc-wide dedupe; BW already
real), `./test.sh` runs the full suite (README + dev-guidelines workflow
updated), `./test.sh` green before this ship. Verified: 33/33 + offscreen.
See: `test.sh`, `pdf_minimalist/core/pipeline.py` (`color_stream_plan`).

## 58 — OPEN (full detail)
Designer: Prev/Next buttons seem to do nothing. Found: `goto_page` scrolled
by stride math, so in the autowrap grid any same-row target computed an
identical scroll value (dead button), and scrolls snapped current back to the
row's first page. Fixed: scroll the target item's scene position (exact for
any grid/mixed sizes); same-row targets still become current. Verified: new
grid walk test + 33/33 green. (Note: on a
1-page doc the buttons are correctly inert.)

## 50 — DONE
~~the navigator section is useless, the original window is the navigator for
now.~~
Stub: OverviewMap widget + label + `_refresh_nav`/`_nav_goto`/nav state
deleted from the right panel; baseline pane is the navigator; view changes
feed only the mini-reframe timer. `overview.py` module kept (covered by
`test_overview_mirrors_view`). Verified offscreen + 27/27 green.
See: `pdf_minimalist/ui_qt/app.py`, `docs/DESIGN.md`.

## 54 — DONE
~~filter details left side should have it [...] sorry, right side~~
Stub: right panel gained a Filter details readout under Preset (threshold +
T, render DPI/page-size/raster, encode line; JPEG q/cap for color; gc note
for Original), refreshed on every control change. Correction: first version
showed implementer jargon `1-bit PNG (JBIG2→G4 planned)` — the designer
ruling (§3 brief + §4) is JBIG2 max compression, so the line now reads the
ruled `JBIG2 · G4 fallback`. Correction 2: the designer never said G4
fallback either (only JBIG2, §4, max compression §3 — verified by grep over
`DESIGNER_VERBATIM.md`; the single G4 hit there is a corpus class, not a
ruling). "G4 fallback" is implementer invention throughout (preset params,
guidelines, design table). UI now reads the ruled `Encode: JBIG2` /
`· JBIG2` with no fallback language. Standing gap (unchanged): Save embeds
1-bit PNG today; the `jbig2` binary is present (`/usr/bin/jbig2`) but unwired
— JBIG2 wiring is outstanding work, est sizes match today's PNG output.
Also fixed latent bug: DPI / page-size / force-raster changes never
dispatched (silently stale) — now they reprocess per §44. Verified offscreen
+ 27/27 green.
See: `pdf_minimalist/ui_qt/app.py` (`_refresh_details`).

## 56 — DONE
~~I also thought that there was a better jpeg compression algo that was widely
supported, better than the default jpg, but of course, not as good as jpeg
xl~~
Stub: JPEG 2000 — proven end-to-end here (Pillow encodes, PyMuPDF embeds
JPXDecode, renders back) and wired as `Color · JPEG2000` (150dpi, rate 24),
listed first among color presets: no JPEG default anymore. Save, preview,
mini, est and details branches included. Bug found live post-ship: the new
JPX mini path called the JPEG preview (throws for jpx) and the worker
swallowed it — one eternal `need_mini=1`, 100% bar, idle CPU. Fixed the
branch + worker failures now log warnings (no more silent stalls) + test
asserts real composites for all 8. MozJPEG noted but not installed.
Verified offscreen + 33/33 green.
See: `pdf_minimalist/core/presets.py`, `pdf_minimalist/core/pipeline.py`
(`jpx_encode`, `recompress_file` codec), `tests/test_pipeline.py`.

## 57 — DONE
~~no jpeg as default, use the best compression tools.  Also, are there options
to use jbig2 or similar with reduces colors index count.~~
Stub: (a) JPX ordered first = default color path, JPEG kept only as fallback
options; (b) few-color images (≤256 distinct colors) get a lossless
palette-quantized Flate candidate that wins whenever smallest — in every
color preset, saver and estimator alike. Verified: FlateDecode picked on flat
logo fixture + smaller file; 32/32 green.
See: `pdf_minimalist/core/pipeline.py` (`indexed_flate_candidate`).

## 56 — OPEN (full detail)
Designer recalls a better-JPEG algo: widely supported, beats default JPG,
below JXL. Verified on this box: (1) MozJPEG (better encoder, same format,
universal) — NOT installed (libjpeg-turbo only); (2) JPEG 2000/JPX (better
codec, in-spec, Acrobat/MuPDF/Evince/Chromium; ~20-30% over JPEG, slower) —
proven end-to-end here (Pillow OpenJPEG encodes, PyMuPDF embeds as JPXDecode,
renders back). Matches existing docs stance (JPX opt-in only). Not yet wired:
needs a `Color · JPEG2000` preset + save/estimate branches + tests.

## 55 — DONE
~~Also, why is proper saving not wired?? I said the size should NOT be
estimate, but be the real amounts, why is this not done and why do you keep
stopping before your work is completed?  Why are you not following my design
rulings???~~
Stub: proper saving IS wired now — `process_file` embeds real JBIG2
(`jbig2 -p` streams as JBIG2Decode XObjects) per your §3/§4 ruling, after I
proved the route (pixel-exact roundtrip) and found + engineered around a real
decoder limitation: small/sparse jbig2enc streams are valid JBIG2 (jbig2dec
clean) but MuPDF cannot complete them (black fill) — every stream is
test-decoded before embedding, failures take 1-bit PNG, per-page codecs
logged at save. Estimator and saver share `bw_page_payload`, so BW captions
are real embedded-byte sums (no `est.`); color stays estimated. 30/30 green
incl. JBIG2 roundtrip, fallback-validity and pixel-exact tests.
See: `pdf_minimalist/core/pipeline.py` (`bw_page_jbig2`, `jbig2_renders`,
`_place_bw`, `process_file`), `tests/test_pipeline.py`.

## 53 — DONE
~~why don't I see the image algorithm?  is that imposed?  It should still be
shown in the filter details.  And is the size based on saving with this
format?  And why estimated?  You should know the exact size of the file once
processing is completed, no?~~
Stub: nothing imposed it — caption space. Each mini now shows name, algorithm
(`otsu · 300dpi · JBIG2`, `JPEG q45 · ≤150dpi`) and full-document payload
estimate (all pages, real save settings, summed; container overhead unknowable
till Save). Exact output size + saving reported after every save. Known
limitation: BW save embeds 1-bit PNG today, JBIG2 wiring outstanding — est
matches today's save output. Verified offscreen + 27/27 green.
See: `docs/DESIGN.md`, `pdf_minimalist/ui_qt/app.py`
(`_preset_algo`, `_reframe_one`, `_on_done`).

## 52 — DONE
~~what is the modern standard keypress for zoom in and zoom out, I tried and
nothing worked.~~
Stub: nothing was bound (only Ctrl+wheel zoomed). Added the modern standard:
Ctrl+Plus in, Ctrl+Minus out, Ctrl+0 fit-width (`=` doubles as `+` on US
layouts); applied to the synced panes. Verified offscreen (in/out/sync/reset)
+ 27/27 green.
See: `pdf_minimalist/ui_qt/app.py` (`keyPressEvent`, `_keyboard_zoom`).

## 51 — DONE
~~WHen I open a new file, the right preview is the last to be updated, it
should be always the first filter to be processed, ahead of all other
priorities.  First open, it would be the first priority filter, but after, it
would be whatever filter the user has selected, right?~~
Stub: yes — priority target is always the active spec (default preset at
first open, selected filter after). `FilterWorker` now renders the active
filter's full preview pages before mini-pages and ests. Verified: emission
order `preview, mini, mini, …` offscreen + 27/27 green.
See: `pdf_minimalist/ui_qt/jobs.py` (`FilterWorker._run`).

## 49 — OPEN (full detail)
Designer: open-file window should show previews of the PDF files; asks if that
needs a custom open-file control. Answer: yes — native dialogs cannot render
PDF pages. Plan (not yet built): non-native dialog (Qt `DontUseNativeDialog`
+ preview pane, or bespoke `QDialog`): directory/file lists left, first-page
thumbnail + page count + size right, rendered via PyMuPDF ~72dpi with an
in-memory thumb cache; double-click opens.
