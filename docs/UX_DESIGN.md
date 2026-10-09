# UX Design — DnD, Visualize, Threshold, ESC

## Main window (v0.1, Tkinter)
```
+--------------------------------------------------------------+
| [Open...] [Save reduced...] [Cancel]  Effort:[Max v]  ESC=?  |
| File: notes.pdf (12 pages, 8.4MB)                            |
+--------------------------------------------------------------+
| Pages |  Preview: [Original|BW @T=180]  Size: 690KB → 41KB   |
|  1 ✓  |  +----------------+ +----------------+               |
|  2 ✓  |  |                | |                |  Strategy:[Otsu]|
|  3 …  |  |  before        | |  after         |  T:[180 ////]  |
|       |  +----------------+ +----------------+  [x] per-page: |
+--------------------------------------------------------------+
| Status: page 4/12…  [Cancel]  (ESC cancels)                  |
+--------------------------------------------------------------+
```

## Interactions
- **Open:** drag PDF onto window (tkdnd if available, else Tk `drop` via
  `xdnd` — fallback is always the Open button; don't block v0.1 on DnD libs),
  or File > Open. Show page thumbnails lazily (render at 72dpi first).
- **Visualize:** click page → render original @150dpi left, processed @150dpi
  right. Zoom fit, 100% toggle. Size labels per page (`orig KB → new KB, %`).
  Global footer: total estimate + progress bar.
- **Threshold:** global slider 0–255 + number entry, live re-preview debounced
  150ms (cancel stale render). Strategy dropdown. "Apply to all" vs per-page
  override: table column with checkbox + spinbox; empty = global.
- **Compress (color mode):** tab `BW | Color`. Color tab: quality slider,
  DPI cap, JPEG/JP2 radio. Same before/after view (JPEG artifacts visible).
- **Save:** never overwrite; suggest `*-reduced.pdf`. Show final bytes + % saved.
- **ESC:** bound on root (`<Escape>`), on dialogs, and on file chooser.
  Also Cancel button. Must work mid-render, mid-encode, mid-save.
  After cancel: partial output deleted, status says "Cancelled at page N".

## LXDE specifics
- Keep window 1024×600-friendly (old laptops), no CSD/headerbar, standard
  Tk theme `clam`, font size 10, high-contrast BW preview (no fancy dark mode v0.1).
- File manager DnD from PCManFM must work — test with `text/uri-list`.
- Low RAM: never hold all pages in memory; render on demand, `del pixmap` + gc.

## Error states
- Encrypted PDF → ask password.
- Born-digital PDF in BW mode → yellow banner: "This PDF has selectable text
  which BW mode will rasterize away. Continue? [Continue] [Use Color mode]".
- Missing `jbig2enc` → info bar: "JBIG2 encoder not found, using G4 (install jbig2enc for smaller files)".
