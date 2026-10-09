# examples/ — PDF optimization test corpus (committed to the repo)

Corpus band (designer §35, supersedes the §24 band for new additions):
**3–50 pages, 200KB–50MB per file.** The nine pre-corpus files (1–2 pages,
`bug1721218*`, `images`, `issue*`, `deed`, `form-fw9`, `manual-maytag`,
`paper-arxiv`, `filled-background`) are grandfathered.
Two requested-type files sit under the 200KB floor — marked (\*) below.

Fetch/validate: `python3 tools/corpus/fetch_and_validate.py` →
`corpus_report.csv` (`OK` / `OUT_OF_RANGE` / `ERROR`). Total: ~127MB, 35 files.

## Corpus table (codecs = embedded image encodings found by the validator)

| file | pages | bytes | profile | codecs |
|---|---|---|---|---|
| `form-941-2026.pdf` | 3 | 841,648 | IRS Form 941: forms, fine lines, small text | none (vector) |
| `worksheet-antietam-jr6.pdf` | 6 | 227,220 | NPS junior-ranger worksheet: simple B&W | Flate-1bit |
| `paper-tracemonkey-pldi09.pdf` | 14 | 1,016,315 | Mozilla paper: fonts, columns, graphs | Flate |
| `models-nasa-observatories.pdf` | 37 | 355,237 | Paper models: ultra-compact line art — leave-alone test | Flate-1bit,JPEG |
| `models-nasa-kepler.pdf` | 12 | 2,262,602 | Technical illustrations | Flate |
| `models-nasa-tess.pdf` | 8 | 1,599,636 | Diagrams and labels | JPEG |
| `coloring-nasa-exoplanets.pdf` | 28 | 4,934,372 | Coloring book: B&W illustration edges | none (vector) |
| `guide-arches-jr-ranger.pdf` | 20 | 5,463,300 | Mixed illustration + text | Flate,JPX |
| `news-crater-lake-2026.pdf` | 8 | 5,550,048 | Photo newspaper, columns | Flate,JPEG |
| `report-unicef-syria-dec2024.pdf` | 9 | 332,700 | Small report, photos/charts — pair with nov (12× bytes!) | Flate,JPEG |
| `report-unicef-syria-nov2024.pdf` | 9 | 4,023,432 | Same type, 12× larger — compression judgment test | JPEG |
| `report-unicef-learning-passport-2025h1.pdf` | 32 | 9,851,153 | Photography, complex layouts | Flate,JPEG |
| `booklet-antietam-jr9.pdf` | 12 | 8,794,410 | Richly illustrated booklet | Flate,JPEG |
| `models-nasa-swift.pdf` | 32 | 15,973,127 | Large print-model file | JPEG |
| `manual-community-gardening.pdf` | 40 | 25,784,891 | Illustrated manual | Flate,JPEG |
| `report-east-point-agri.pdf` | 43 | 27,051,723 | Large photo-rich planning report | Flate,JPEG |
| `scan-naca-report820.pdf` | 23 | 1,660,774 | 1945 aged print: graphs, equations, artifacts | Flate-1bit |
| `scan-nara-dod-schedule.pdf` | 12 | 1,130,733 | Modern cover + historic scans, dirty borders, speckle | Flate-1bit,JPEG |
| `scan-jfk-handwritten-index.pdf` | 30 | 1,069,151 | Forms + handwriting, variable contrast | Flate-1bit |
| `scan-jfk-surveillance-notes.pdf` | 9 | 335,232 | Small cursive, ink strokes, speckles | Flate-1bit |
| `scan-jfk-ruled-list.pdf` | 35 | 1,785,051 | Faded ruled lines, sparse handwriting | Flate-1bit |
| `scan-jfk-dark-letter.pdf` | 6 | 3,980,142 | Severely degraded, dark background — threshold torture test | Flate-1bit |
| `scan-jfk-poor-copies.pdf` | 8 | 349,667 | Faint broken characters, low contrast | Flate-1bit |
| `scan-naca-tm972.pdf` | 11 | 374,461 | Aged typewriting, annotations, diagrams | Flate-1bit |
| `scan-naca-tm997.pdf` | 23 | 787,836 | Formulas, weak print, noise, graphics | Flate-1bit |
| `scan-naca-formulas.pdf` | 7 | 257,739 | Heavy type, math symbols, small marks | Flate-1bit |
| `images.pdf` | 1 | 1,494,439 | Photo-heavy + text (pre-corpus) | JPEG |
| `issue1905.pdf` | 1 | 918,339 | Mixed 8 images + text (pre-corpus) | JPEG |
| `issue13520.pdf` | 1 | 754,579 | Tiny vector snippet (pre-corpus) | vector |
| `bug1721218_reduced.pdf` | 1 | 825,329 | 3522 vector drawings (pre-corpus) | vector |
| `deed-brevard.pdf` | 2 | 144,058* | Recorded warranty deed, signed scan (pre-corpus) | scan |
| `form-fw9.pdf` | 6 | 140,815* | IRS W-9 + instructions (pre-corpus) | text |
| `manual-maytag-dryer.pdf` | 2 | 1,503,636 | Appliance quick-start EN/FR (pre-corpus) | JPEG |
| `paper-arxiv-1406.2661.pdf` | 9 | 530,482 | Research paper, 6 figures (pre-corpus) | JPEG |
| `filled-background.pdf` | 3 | 401,129 | 3-page scroll test (pre-corpus) | vector |

Not fetched: `report-cdc-births-deaths.pdf` (CDC stacks returns 403 to scripts —
validator status ERROR; direct browser download works).

## Manual leads (no direct multipage PDF — not auto-downloaded)

- Arizona Republican 1908-08-19 (10 newspaper pages): https://www.loc.gov/resource/sn84020558/1908-08-19/ed-1/
- Andrew Jackson correspondence 1814 (12 manuscript pages): https://www.loc.gov/resource/maj.01022_0298_0309/
- 17th-c. Spanish legal brief (10 pages): https://www.loc.gov/resource/llhsp.llhsp_brief_04-00441-00445/

## Spot-checks 2026-10-09 (outputs to gitignored `.tmp/`, not committed)

- Pre-corpus: `bug1721218` BW otsu −98% · `images` color q45 −88% · `issue1905` color q45 −20%.
- Scans with current PNG-embedded 1-bit (no JBIG2 yet): `scan-jfk-dark-letter`
  3,980,142 → 5,142,092 (**+29% bigger**), `scan-naca-report820` 1,660,774 →
  2,472,530 (**+49% bigger**). Honest signal for two rulings: the optimizer must
  sometimes decline to "optimize" (§35), and JBIG2 wiring is now the top
  compression gap (queue).
