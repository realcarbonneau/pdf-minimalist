# DESIGN — preset filter-strip + comparison views

## Designer rulings (verbatim)
Quoted exactly from `DESIGNER_VERBATIM.md`. Do not edit the quotes.

Ruling §3 — original brief:
> I want to make a simple app that works on multiple platforms, but first targetting lxde debian linux.  I want to dnd or open a pdf docs and be able to visualize various optimizations to it.  Highly opinionated, eg conversion to BW with a few strategies and a global or per page threshold, like GIMP threshold option.  Also, another option that compresses images within the pdf to jpg XL or whatever highest compression algorithms exist.  Same for BW, JDIC2 (I think if I remeber correctly.  Always max compression for all by default, but tunable if too slow.  Always fast cancel with esc by user as required.  Start by making some md docs directly in this dir with your notes, ideas and tests.

Ruling §6 — picky UI:
> what if I am really picky about smooth clean custom UI highly tailored for a specific job, like pan, zoom in/out mouse scroll, next page, prev page, DnD, etc.

Ruling §9 — preset filter-strip + view options:
> I want to see a list of preset optimization options, like photo filters on a camera with a smaller version of previews, and when I click on one, the main doc has original and preview (optmized side by side, vertically or horizontally, same for the filter thumbnails, all would be choosable as menu view options.

Ruling §10 — raster defaults on main screen:
> Generally forcing alll images on the page and page rasterizing to 300dpi, and 8.5x11, but that also would be options on the main screen.

## Concept (camera-filter UX for PDFs)
- Left/bottom **filter strip**: every preset renders a small live thumbnail of the
  CURRENT page through its pipeline. Click a thumbnail = select preset → main panes update.
- **Main panes**: original (left/top) + optimized preview (right/bottom) of the same page.
- **View menu** controls orientation of main panes AND of filter thumbnails:
  - `View → Main: Side by side (H) | Stacked (V) | Single (toggle Orig/Preview)`
  - `View → Filters: Filmstrip (H) | Rail (V) | Grid`
  - Shortcuts: `Ctrl+1/2/3` main modes, `Ctrl+Shift+H/V/G` filter layout.
  - Zoom keys (designer ruling §52, modern standard): `Ctrl+Plus` in,
    `Ctrl+Minus` out, `Ctrl+0` fit-width. Panes stay synced either way.
  - Choice persists in QSettings.

```
View=Main:H + Filters:H (default, wide screen)
+---------------------------------------------------------+
| Pages | Original   | Preview (preset: BW Otsu) | Preset |
|  1    |            |                           | [oto]  |
|  2    |  before    |  after                    | [T180] |
+---------------------------------------------------------+
| Filters (filmstrip H): [orig][otsu][T180][T210][sauv][Cmax][Cbal] |
+---------------------------------------------------------+
View=Main:V + Filters:V (square / portrait screens) → panes stacked, rail on right.
```

## Preset list (v0.1 — opinionated, max-compression default)
| # | Preset (label) | Mode | Params | Use when |
|---|---|---|---|---|
| 0 | Original (no-op) | — | gc+deflate only | baseline / born-digital keep |
| 1 | BW · Otsu Auto ★ default | BW | 300dpi, otsu, JBIG2 | most scans |
| 2 | BW · Clean T=180 | BW | 300dpi, simple T=180 | clean laser prints |
| 3 | BW · Strong T=210 | BW | 300dpi, simple T=210 | faint pencil / gray bg |
| 4 | BW · Stained Paper | BW | 300dpi, sauvola w31 k0.25 | yellowed / uneven light |
| 5 | BW · Fast Draft | BW | 200dpi, otsu, JBIG2 | old hardware, quick pass |
| 6 | Color · JPEG2000 ★ default color | JPX | 150dpi, rate 24 | smallest photos, slower |
| 7 | Color · Max Squeeze | JPEG | 150dpi, q45 4:2:0 | smallest slides/photos |
| 8 | Color · Balanced | JPEG | 200dpi, q60 | readable photos, fewer blocks |

Few-color images (designer ruling §57: ≤256 distinct colors — logos,
diagrams, flat screenshots) take a lossless palette-quantized Flate version
whenever it beats the codec re-encode, in every color preset.

Defined in code: `pdf_minimalist/core/presets.py` → `PRESETS` (id, label, mode, params).
Thumbnails render lazily at ~96px on page change (debounced 150ms, cancellable);
main preview re-renders at 150dpi on preset click (300dpi at Save).

## Behavior
- Left pane is always the unmodified baseline (no baseline variants); right
  pane shows the selected filter. The strip shows one live mini per filter of
  the current page — Original excluded, the left pane is the baseline
  (designer ruling §30).
- Panes always synced (designer ruling §22): zoom, pan, and scroll in either
  main pane mirror to the other instantly.
- Continuous viewer, no page list (designer ruling §26): both panes scroll
  through ALL pages vertically with a 24px gap; the left page list is gone and
  the status bar shows `Page N of M` from scroll position instead.
- Autowrap grid: zooming out reflows pages into as many columns as fit the
  window width (`cols = floor(viewport_w / (page_w * zoom + gap))`, min 1);
  zooming in returns to single-column. Both panes compute the same columns.
- PgUp/PgDn jump to prev/next page top; click a filter mini still switches
  the right pane's filter (radio-behavior); minis render the current
  (top-visible) page.
- Sizes under minis (designer ruling §32, real amounts §§55/59): each strip
  mini carries its filter recipe (threshold strategy, DPI, encoder — `§53`)
  and the FULL-document real amount with the exact save bytes — BW sums the
  embedded page payloads, color sums the exact per-image save decisions
  (doc-wide dedupe included). No estimates anywhere; PDF container/gc
  overhead is reported with the exact output size after every save.
- Navigator dropped (designer ruling §50): the separate OverviewMap navigator
  is gone — the original (left) window is the navigator. The right panel keeps
  preset, strategy, threshold, DPI, page-size, force-raster, page buttons,
  Save and Cancel; page/progress/status stay in the status bar.
- One panel + menu (designer ruling §32): no left panel. File actions live in
  the menu; all working controls live in the single right panel; page/progress
  /status live in the status bar.
- Background rendering, never frozen GUI (designer ruling §37): every
  per-preset job (viewport minis, est. sizes, full preview pages) runs in
  separate worker PROCESSES (spawn context, capped at half the cores — a real
  cap with real parallelism), managed by a thin QThread that only forwards
  results with the dispatch generation. Rationale, verified by bisection:
  GUI-thread rendering froze the app; a thread pool then aborted bare inside
  numpy with Qt signals in play (isolated numpy, isolated fitz and paired
  thread-workers all survive — only the full threaded path aborts), so threads
  are out for compute. Pan/zoom never re-renders: purely a view transform
  over already-rendered pixmaps.
- Thumbnails = exact mini of the main view (designer ruling §48, intent §32
  + §37 + §45): each strip mini shows EXACTLY what the synced main windows
  show — same pages, same grid, same scroll framing down to the cut-off last
  page — but rendered through that mini's own filter from its internally
  preprocessed file (built in background at start / latest change). Scroll,
  pan and zoom are pure view changes: minis re-frame from cached per-preset
  pages with zero background jobs (§47). A new job runs only on file change
  or filter-spec change (§44).
- Strip style (designer ruling §46): each mini sits in a clear bordered
  preview box; a divider line separates it from the caption below, where the
  filter name and est. size print in smaller characters.
  Stale jobs are abandoned by generation counter, never applied. Filter sort +
  max-auto-filters: deferred, explicitly later.
- Per-filter progress (designer ruling §43): EACH strip filter shows its own
  progress in place — `working…` → mini shown (50%) → `est. X` shown (100%).
  The status-bar bar keeps only the aggregate job progress; it never replaces
  the per-filter bars.
- Process-once cache (designer ruling §44): a filter result is computed once
  per (file identity + page + viewport crop + filter spec) and reused.
  Clicking the strip or preset combo with an unchanged key switches panes
  instantly with NO new background job. A new job runs only when the file
  (path + mtime + size) or the spec (preset id/params, T/strategy, DPI,
  page-size, force-raster) or the page/crop changes.
- Per-page override (brief §3): page remembers its preset; empty = current global.
- ESC cancels thumbnail batch + save job alike (<200ms, partial output deleted).
- Born-digital warning: selecting a BW preset on a text-layer page shows the
  yellow banner (rasterizes text away) with [Continue] [Use Color instead].
