# Designer directives — VERBATIM

> Preservation rule: the quotes below are the designer's own words,
> copied exactly, typos and all. Do NOT fix spelling, grammar, or punctuation.
> Do NOT paraphrase. If you need a corrected term (e.g. JDIC2 → JBIG2), add it
> in brackets outside the quote. New designer comments get appended
> here with date + full verbatim text.

## 1 — tooling
> is my opencode harness up to date?  How do I update it?

## 2 — tooling
> user@main:~/Downloads/pdf-reducer$ opencode update
> Error: Failed to change directory to /home/user/Downloads/pdf-reducer/update
> user@main:~/Downloads/pdf-reducer$

## 3 — app vision (original brief)
> I want to make a simple app that works on multiple platforms, but first targetting lxde debian linux.  I want to dnd or open a pdf docs and be able to visualize various optimizations to it.  Highly opinionated, eg conversion to BW with a few strategies and a global or per page threshold, like GIMP threshold option.  Also, another option that compresses images within the pdf to jpg XL or whatever highest compression algorithms exist.  Same for BW, JDIC2 (I think if I remeber correctly.  Always max compression for all by default, but tunable if too slow.  Always fast cancel with esc by user as required.  Start by making some md docs directly in this dir with your notes, ideas and tests.

## 4 — codec name
> Yes, JBIG2, summarize your suggestions to me

## 5 — frameworks
> lok, no jxl.   rank the frameworks by the size of dependencies and range of os/wm support.

## 6 — picky UI
> what if I am really picky about smooth clean custom UI highly tailored for a specific job, like pan, zoom in/out mouse scroll, next page, prev page, DnD, etc.

## 7 — Qt check
> seems like Qt is really solid, can you double check?

## 8 — local vs system
> ok, start with that, I already stated alot of my objectives.  Can you put everything local in this directory?  Tell me what is local and what needs to be system packages?

## 9 — this request (verbatim, 2026-10-09)
> Put all my comments verbatim in a design md doc, make a docs dir.  make a dev md doc with guidance, including to keep all my comments verbatim.  I want to see a list of preset optimization options, like photo filters on a camera with a smaller version of previews, and when I click on one, the main doc has original and preview (optmized side by side, vertically or horizontally, same for the filter thumbnails, all would be choosable as menu view options.

## 10 — raster defaults (verbatim, 2026-10-09)
> Generally forcing alll images on the page and page rasterizing to 300dpi, and 8.5x11, but that also would be options on the main screen.

## 11 — docs terminology (verbatim, 2026-10-09)
> design.md, designer rulings section, verbatim.  In the docs, always call the operator/user the designer.

## 12 — finish work + TODO log (verbatim, 2026-10-09)
> yes, finish prior work, and every request put in a TODO.md doc numbered list, never renumbered, so you don't forget things.

## 13 — dev guidance rulings (verbatim, 2026-10-09)
> developement guidelines has my ruling for general guidelines, including the todo instructions.

## 14 — run UI + stdout logging + --debug (verbatim, 2026-10-09)
> run the ui please so I can see.  The app should log everything important to the stdout so that you can run and review what happened from the log.  Also, have a --debug mode that dumps more so you can rune and evaluate issues and problems as required.  This goes in development guidelines, as it is not a ui nor feature design issue.

## 15 — stay local (verbatim, 2026-10-09)
> don't go outside the local dir, make a local ./.tmp/ and gitignore it.  Later we will push to github.

## 16 — todo format + dropped log (verbatim, 2026-10-09)
> no checkbox for doto list, put item in full detail, when completed, stub, cross ref with final docs that implement it and strikethrough.  If dropped, we can have a doc with dropped ideas and log them for historical reference with reasons.  Once we do work, we don't want to redo the work and knowledge.

## 17 — full developer guidelines doc (verbatim, 2026-10-09)
> call it the full developper guidlines md doc

## 18 — docs to docs dir (verbatim, 2026-10-09)
> move most of your docs to the docs dir please

## 19 — docs lead (verbatim, 2026-10-09)
> yes, correct docs, don't ask, docs should be all updated first, then dev work.  Docs lead the decisions, rulings, design intent.  Everything else follows.

## 20 — continue (verbatim, 2026-10-09)
> continue, why did you stop?

## 21 — run it or not ready (verbatim, 2026-10-09)
> run the app, or it's not reaady?

## 22 — synced panes (verbatim, 2026-10-09)
> page zoom, pan, etc is always synced on both panes

## 23 — baseline left, filters right (verbatim, 2026-10-09)
> left side is baseline, so no preview of basline, right side is per filter.

## 24 — example PDFs (verbatim, 2026-10-09)
> find a few public pdf docs that are representative test cases, not too big, 1 to 10 pages, 200k to 10 mb, put in examples dir in this repo

## 25 — scroll convention (verbatim, 2026-10-09)
> also ctl mouse scroll is up/down?  Or mouse scroll is page scroll and ctl wheel is zoom, I think that is more common ui, no?

## 26 — continuous viewer (verbatim, 2026-10-09)
> the page viewer should be continuous by default, with a gap between paged.  No page list to the left.  Zoom out should aso autowrap to multiple pages per side if it fits in the window width.  Do you follow?

## 27 — real examples (verbatim, 2026-10-09)
> Did you find example pdfs?  Your pdf file is not a good example at all.

## 28 — 3-page example (verbatim, 2026-10-09)
> use a 3 page example for the tests please.

## 29 — more real-world types (verbatim, 2026-10-09)
> Why are there only 5 examples in the repo?  There are many types of pdf available on the internet, deeds, research papers, documentations, appliance manuals, etc...

## 30 — original in filters (verbatim, 2026-10-09)
> Also, why is original still in the filters?  Or did you not relaunch the latest version?

## 31 — terrible default pdf (verbatim, 2026-10-09)
> why are you using that terrible pdf as a default?

## 32 — sizes, navigator, one panel (verbatim, 2026-10-09)
> the app should show the final size of each filter below it.  It should also show the small preview which is mirroring the current view on the original.  Remove the left panel and put the options in the menu or in the right panel, there will only be one tool panel and a menu.

## 33 — drop top labels (verbatim, 2026-10-09)
> Don't show the tooltips at the top, waste of space, we will find another place for that

## 34 — fit right or menu (verbatim, 2026-10-09)
> For now, fit everything you can on the right side panel or in the menu.

## 35 — optimization test corpus brief (verbatim, 2026-10-09)
> document, compile and collect these, document in an examples md doc with descriptions, view them also.  # PDF optimization test corpus — initial collection
>
> I'll target 18–24 public PDFs, with a strict range of 3–50 pages and 200 KB–50 MB per file. The objective is to find documents that stress different parts of a PDF optimizer, not merely different subject matter.
>
> ## 1. Categories and sources
>
> | Category                                  | Target sources                                     | What we'll test                                             |
> | ----------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------- |
> | 1. Text-heavy research papers             | arXiv, universities, Mozilla                       | Font embedding, text preservation, equations                |
> | 2. Forms and structured documents         | IRS, government agencies                           | Fine lines, form fields, tables                             |
> | 3. Vector diagrams and technical drawings | NASA, USGS, engineering documents                  | Preserving vector precision and small labels                |
> | 4. Photo-heavy publications               | NASA, National Park Service                        | JPEGli vs. JPEG 2000, image downsampling                    |
> | 5. Mixed-layout brochures                 | NPS, museums, visitor guides                       | Photos, graphics, colored text on the same page             |
> | 6. B&W scanned documents                  | Library of Congress, Internet Archive              | Fixed/adaptive thresholds, JBIG2                            |
> | 7. Old books and newspapers               | Digital libraries, historic archives               | Yellowed paper, bleed-through, faded type                   |
> | 8. Illustrated educational books          | NASA, public educational resources                 | Color illustrations, line art, large graphics               |
> | 9. Scientific maps and charts             | USGS, NOAA                                         | Fine labels, dense linework, mixed raster/vector content    |
> | 10. Corporate-style reports               | Public annual/impact reports                       | Charts, branding, transparency, font subsets                |
> | 11. Manuals and instructions              | Open-source projects, hardware vendors             | Screenshots, diagrams, repetitive images                    |
> | 12. PDF compatibility edge cases          | PDF.js, PDF Association, accessibility test suites | Annotations, metadata, transparency, special PDF structures |
>
> I'll deliberately include both already-optimized PDFs and visibly inefficient ones. A good optimizer should sometimes report that it cannot improve a file without unacceptable quality loss.
>
> ## 2. First selection: 22 candidate PDFs found
>
> Here are 17 of the strongest candidates. These are links to the actual PDFs, not just search pages.
>
> Sizes are publisher-listed or approximate; page counts have been checked directly for many of the smaller files. Larger files still need download-side verification.
>
> | PDF / source                                                                                                                                 | Pages | Listed size | Optimization challenge            |
> | -------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ----------- | --------------------------------- |
> | [IRS Form 941 (2026)](https://www.irs.gov/pub/irs-pdf/f941.pdf)                                                                              | 3     | 822 KB      | Forms, fine lines, small text     |
> | [Antietam Junior Ranger (ages 6 and under)](https://home.nps.gov/anti/learn/kidsyouth/upload/2018july25Jr-ranger-under-six-508-1.pdf)        | 6     | 222 KB      | Simple B&W worksheets             |
> | [Mozilla TraceMonkey paper](https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf)                                         | 14    | \~1 MB      | Fonts, text columns, graphs       |
> | [CDC: Trends in Births and Deaths](https://stacks.cdc.gov/view/cdc/174614/cdc_174614_DS1.pdf)                                                | 12    | 366 KB      | Vector charts and tables          |
> | [NASA Great Observatories models](https://science.nasa.gov/wp-content/uploads/2023/05/HST_Compton_Chandra_PaperModels.pdf)                   | 37    | 348 KB      | Very compact line-art baseline    |
> | [NASA Kepler model](https://science.nasa.gov/wp-content/uploads/2023/05/2017_Kepler_Paper_Models.pdf)                                        | 12    | 713 KB      | Technical illustrations           |
> | [NASA TESS model](https://science.nasa.gov/wp-content/uploads/2023/05/TESS_Paper_model_v2-1.pdf)                                              | 8     | 1.6 MB      | Diagrams and labels               |
> | [NASA Exoplanets coloring book](https://science.nasa.gov/wp-content/uploads/2023/10/Exoplanets_Coloring_Book_07-22-2016.pdf)                 | 28    | \~5 MB      | B&W illustration edges            |
> | [Arches Junior Ranger guide](https://www.nps.gov/arch/planyourvisit/upload/Arches-Junior-Ranger-web.pdf)                                     | 20    | \~5 MB      | Mixed illustration and text       |
> | [Crater Lake Reflections (2026)](https://www.nps.gov/crla/learn/news/upload/Crater_Lake_Reflections_Summer-Fall_2026_Low-Res_508.pdf)        | 8     | 5.29 MB     | Photos, newspaper columns         |
> | [UNICEF Syria report, December 2024](https://www.unicef.org/syria/media/19811/file/Syria-Humanitarian-situation-report-29-December-2024.pdf) | 9     | 333 KB      | Small report with photos/charts   |
> | [UNICEF Syria report, November 2024](https://www.unicef.org/syria/media/19821/file/Syria-Humanitarian-situation-report-November-2024.pdf)    | 9     | \~4 MB      | Larger report of similar type     |
> | [UNICEF Learning Passport report](https://www.unicef.org/learningpassport/media/1606/file/Jan.-June%202025%20Progress%20Report.pdf.pdf)      | 32    | \~10 MB     | Photography and complex layouts   |
> | [Antietam Junior Ranger (ages 9+)](https://home.nps.gov/anti/learn/kidsyouth/upload/Jr-Ranger-Booklet-2023-section-508.pdf)                  | 12    | 8.4 MB      | Richly illustrated booklet        |
> | [NASA Swift model](https://science.nasa.gov/wp-content/uploads/2023/05/swmodguide5.pdf)                                                      | 32    | 15.2 MB     | Larger print-model file           |
> | [Community Gardening Manual](https://cdn.atlantaregional.org/wp-content/uploads/communitygardeningmanual-june2022.pdf)                       | 40    | 25 MB       | Illustrated manual                |
> | [East Point Agriculture Plan](https://cdn.atlantaregional.org/wp-content/uploads/east-point-city-agriculture-plan.pdf)                       | 43    | 26 MB       | Large, photo-rich planning report |
>
> Sources for the listed sizes and page counts include NASA's model catalog, NPS publication pages, UNICEF's reports, CDC's archive and the Atlanta Regional Commission.
>
> The full manifest also includes an architectural archive, a NIST standards document, an Arduino datasheet, a USGS geoscience document and a CDC medical journal.
>
> ## 3. Corpus starter files
>
> Download PDF test corpus starter
>
> 22 source records · JSON manifest · Python downloader/validator · README
>
> The package contains source links rather than copies of the PDFs. Its validator checks actual download sizes, page counts, SHA-256 hashes and embedded image compression types.
>
> You can also get the individual files:
>
> PDF manifest (JSON) · Download/validation script (Python)
>
> Run on Debian/LXDE:
>
> ```
> sudo apt install python3 poppler-utils
> python3 fetch_and_validate.py manifest.json ./downloads
> ```
>
> It creates `downloads/corpus_report.csv`, with `OK`, `OUT_OF_RANGE`, or `ERROR` for each candidate. I created and syntax-checked the script, but couldn't execute the remote downloads in this environment.
>
> ## 4. What I particularly want to measure
>
> For each qualifying PDF, the next useful measurements will be:
>
> | Metric                          | Reason                                      |
> | ------------------------------- | ------------------------------------------- |
> | Total file size / page          | Basic compression benchmark                 |
> | Embedded image count and codecs | Determine JPEG, JPX, JBIG2, Flate, etc.     |
> | Largest embedded images         | Identify high-impact candidates             |
> | Text and vector preservation    | Avoid destructive full-page rasterization   |
> | Estimated B&W suitability       | Identify pages worth thresholding           |
> | Before/after visual differences | Detect unacceptable quality loss            |
> | Compression ratio by strategy   | Compare JPEGli, JPEG2000, grayscale, JBIG2 |
>
> Two comparisons stand out already: the UNICEF reports show how similarly sized documents in page count can differ dramatically in bytes, while the NASA models show that dozens of illustration-heavy pages can fit in only a few hundred kilobytes. They should help test whether the optimizer knows when to compress and when to leave a well-optimized PDF alone.
>
> The remaining priority gap is a set of genuinely scanned, noisy historic pages with confirmed 1-bit, grayscale, or color raster content. Those will be critical for evaluating your fixed-threshold, Sauvola/Otsu and lossless-JBIG2 pipelines.

## 36 — historical scan test set (verbatim, 2026-10-09)
> ## Confirmed additions: historical scan test set
>
> I've now located actual scanned-document candidates, including one particularly useful example of dirty scan borders.
>
> | Document                                                                                                                                                                                                                  | Pages | Why it's useful                                                                                  |
> | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------------------------------------------------------------------------------------------------ |
> | [NACA Report 820 — Propellers in Yaw (1945)](https://ntrs.nasa.gov/api/citations/19930091897/downloads/19930091897.pdf)                                                                                                   | 23    | Aged printing, fine graph lines, equations, scan artifacts and imperfect text                    |
> | [National Archives — Defense Department records schedule](https://www.archives.gov/files/records-mgmt/rcs/schedules/departments/department-of-defense/office-of-the-secretary-of-defense/rg-0330/nc1-330-78-07_sf115.pdf) | 12    | Mixed modern cover pages and historical scanned pages, dirty borders, speckling and uneven print |
>
> I checked the actual PDF page counts and inspected rendered pages from both. Their download sizes still need verification.
>
> These are the kinds of PDFs where threshold settings, despeckling, border removal and JBIG2 compression can make a meaningful difference — and where an overly aggressive threshold can destroy faint information.
>
> ## Additional verified scanned PDFs
>
> The National Archives' JFK records turn out to be an excellent source of real-world processing failures: handwritten documents, degraded photocopies, repeated office forms, ruled paper, and badly reproduced originals.
>
> | Direct PDF                                                                                                           | Pages | Primary test                                         |
> | -------------------------------------------------------------------------------------------------------------------- | ----- | ---------------------------------------------------- |
> | [CIA handwritten index/file requests](https://www.archives.gov/files/research/jfk/releases/2018/104-10079-10231.pdf) | 30    | Forms, handwriting, variable contrast                |
> | [Handwritten surveillance notes](https://www.archives.gov/files/research/jfk/releases/2018/104-10196-10045.pdf)      | 9     | Small cursive text, ink strokes, speckles            |
> | [Handwritten list on ruled paper](https://www.archives.gov/files/research/jfk/releases/2018/104-10054-10408.pdf)     | 35    | Faded lines, very sparse handwritten content         |
> | [Handwritten letter and attachments](https://www.archives.gov/files/research/jfk/releases/2018/104-10071-10069.pdf)  | 6     | Severely degraded reproduction, very dark background |
> | [Poor-copy handwritten summaries](https://www.archives.gov/files/research/jfk/releases/104-10196-10330.pdf)          | 8     | Faint, broken characters and low contrast            |
> | [NACA Technical Memorandum 972 (1941)](https://ntrs.nasa.gov/api/citations/19930094444/downloads/19930094444.pdf)    | 11    | Aged typewriting, annotations and diagrams           |
> | [NACA Technical Memorandum 997 (1941)](https://ntrs.nasa.gov/api/citations/19930094420/downloads/19930094420.pdf)    | 23    | Formulas, weak print, noise and graphics             |
> | [NACA boundary-layer formulas (1941)](https://ntrs.nasa.gov/api/citations/19930092712/downloads/19930092712.pdf)     | 7     | Heavy type, mathematical symbols and small marks     |
>
> All eight page counts were confirmed from the actual PDF documents, and I inspected representative rendered pages.
>
> The dark handwritten letter is especially valuable: automatic thresholding may make it worse. It provides a strong test for local contrast enhancement, background estimation and page-specific settings rather than blindly applying a global threshold.
>
> ## Historical newspapers and older manuscripts
>
> I also found a few useful Library of Congress collections:
>
> - [Arizona Republican, August 19, 1908](https://www.loc.gov/resource/sn84020558/1908-08-19/ed-1/) — 10 newspaper pages, dense columns and historical printing.
> - [Andrew Jackson correspondence, 1814](https://www.loc.gov/resource/maj.01022_0298_0309/) — 12 manuscript pages.
> - [Seventeenth-century Spanish legal brief](https://www.loc.gov/resource/llhsp.llhsp_brief_04-00441-00445/) — 10 pages of historical printed material.
>
> These are source records, not yet verified multipage PDF download files. Some Library of Congress viewers provide individual page PDFs instead of a combined document, so I've kept these separate from the automated downloads.
>
> ## Updated test corpus
>
> Download updated PDF corpus package
>
> 32 direct PDF candidates · 10 historical scans · 5 additional archive leads · validator
>
> Updated JSON manifest · Validation script
>
> The remaining limitation is actual file size verification. I confirmed the page counts and visually examined the scanned documents, but remote PDF downloads were unavailable in this workspace. The validator will enforce the requested 200 KB–50 MB range and identify image codecs on a network-connected machine.
>
> For the optimizer itself, I would make the faint handwriting, dark photocopies, and ruled-paper scans mandatory regression tests. They are substantially more revealing than clean PDFs when evaluating threshold strategies and JBIG2 compression.

## 37 — background previews (verbatim, 2026-10-09)
> don't freeze the whole app when doing the previews, do it in background.  the thumnail previews have to show the same viewport.  I want the app to do the full processing of each preset in the background without freezing the system, maybe set a max cores usually at 50% of the system if the processing is one core at a time (is it?) and then when panning, you are just showing a view on the rendered file.  Show a progress bar on each file that is processing.  Later, we will have an option to sort the filters and set a max auto filters, or no max.

## 38 — corpus audit: camera-captured documents (verbatim, 2026-10-09)
> # Corpus audit: the biggest gap is real camera-captured documents
>
> I reviewed all 32 direct-PDF candidates in the current manifest, plus the five Library of Congress discovery leads.
>
> The collection is overly concentrated in NASA illustrations, historical aerospace scans, and National Archives paperwork. It has good coverage of ordinary PDFs, but almost no material designed to test difficult lighting in photographs of paper documents.
>
> A faded archival scan is not equivalent to a phone photograph taken under a desk lamp. The latter may have white paper in shadow that's darker than ink elsewhere on the same page. A single global threshold cannot reliably separate those pixels.
>
> ## 1. What I'd consolidate
>
> | Overlapping group               | Current count | Recommendation                                                      |
> | ------------------------------- | ------------- | ------------------------------------------------------------------- |
> | NASA spacecraft models          | 4             | Keep Great Observatories and TESS; move Kepler and Swift to reserve |
> | NARA JFK records                | 5             | Keep dark photocopy, faint handwriting, and ruled-paper examples    |
> | Historic NACA technical reports | 4             | Keep Propellers in Yaw and TM 997                                   |
> | CDC publications                | 2             | Keep the statistical-charts report; move MMWR to reserve            |
> | Atlanta planning manuals        | 2             | Keep the 43-page East Point plan                                    |
> | NPS activity booklets           | 3             | Keep a small B&W worksheet and one richly illustrated booklet       |
>
> I would retain both 9-page UNICEF Syria reports for now. Their large advertised size difference makes them a useful controlled comparison, provided inspection confirms meaningfully comparable content.
>
> That reduces the primary set from 32 to approximately 22–23 PDFs, before adding the missing classes. These are coverage-based decisions, not claims that the removed files are bad test material.
>
> ## 2. The hardest missing test cases I've found
>
> 1\. [DocShadow-SD7K](https://cxh-research.github.io/DocShadow-SD7K/) — highest priority
>
> Real photographs of documents under difficult shadows, with corresponding shadow-free reference images. The researchers collected over 7,000 high-resolution pairs using different lighting conditions and occluders.
>
> Stress: bright paper beside deep shadows, partial line obscuration, and preservation of tiny text.
>
> The compressed full dataset is still about 9 GB; I'd extract a small, carefully selected subset rather than include the whole dataset.
>
> 2\. [SmartDoc 2015](https://github.com/jchazalon/smartdoc15-ch1-dataset) — most practical phone-photo benchmark
>
> Smartphone video frames containing printed letters, magazine pages, patents, tax documents, scientific papers, and datasheets, with blur, lighting changes, perspective distortion, and partial occlusion.
>
> Stress: detecting the paper region and deciding whether to crop, rectify, normalize lighting, or preserve the photograph.
>
> This dataset is explicitly licensed CC BY 4.0.
>
> 3\. [DocUNet](https://www3.cs.stonybrook.edu/~cvl/docunet.html) — curved and warped pages
>
> Real camera photographs of curved document pages, paired with flatbed scans and cropped versions.
>
> Stress: gutter shadows, curved text baselines, local blur, perspective, and page-shape changes. The original-photo download is listed at 328 MB.
>
> 4\. [DIBCO 2019](https://vc.ee.duth.gr/dibco2019/) — objective B&W threshold tests
>
> Historical handwritten and printed documents with degraded backgrounds and reference binary images. This lets us quantify missed ink and false black pixels instead of relying entirely on visual judgment.
>
> 5\. [SSD-DIS (2026)](https://doi.org/10.6084/m9.figshare.29401811) — diverse shadow shapes
>
> A newer semi-synthetic document shadow dataset including text, graphics, handwriting, and multilingual pages. It offers a controlled complement to real-camera images.
>
> These are publicly available image datasets, not ready-made multipage PDFs. For your optimizer, the proper approach is to assemble subsets of 3–50 original images into image-only PDFs, keeping source filenames and reference images outside the PDF for testing.
>
> ## 3. Additional classes missing from the original corpus
>
> Beyond the difficult photographs, the following deserve separate tests:
>
> | Priority | Missing class                                         | Why it matters                                                    |
> | -------- | ----------------------------------------------------- | ----------------------------------------------------------------- |
> | Critical | Uneven illumination and flash glare                   | A global B&W threshold can erase text or turn shadows black       |
> | Critical | Book gutter and curved pages                          | Requires illumination correction and possibly dewarping           |
> | High     | Scanned PDF with invisible OCR text                     | Optimization must preserve selectable/searchable text             |
> | High     | Already-compressed JBIG2, CCITT and MRC PDFs          | Avoid making highly optimized PDFs larger or worse                |
> | High     | CMYK, ICC profiles, transparency                      | Prevent color changes and rendering errors                        |
> | High     | PDF/A, PDF/UA and tagged documents                    | Preserve archival and accessibility properties                    |
> | High     | Digital signatures, annotations and interactive forms | Avoid damaging document functionality                             |
> | High     | Mixed per-page codecs and shared image objects        | Verify that page-specific optimization doesn't change other pages |
>
> The [PDF Association's PDF corpora index](https://github.com/pdf-association/pdf-corpora) is a good source for these structural tests, including PDF/A, PDF/UA, PDF/X, and rendering compatibility suites.
>
> ## 4. What the hardest photographed documents should test
>
> I'd test the following sequence against each photographed page:
>
> Processing ladder
>
> 1. Original color image — preservation baseline
> 2. Grayscale, without thresholding
> 3. Fixed global threshold
> 4. Otsu automatic threshold
> 5. Sauvola / Wolf adaptive threshold
> 6. Background illumination correction, then adaptive threshold
> 7. Retain grayscale or color if B&W destroys information
>
> The last option is essential. If a dark shadow and actual ink have overlapping brightness values, a simple global threshold cannot correctly distinguish them. If glare has clipped image detail entirely, even sophisticated software cannot reliably recover it.
>
> For your application, I would make “B&W not recommended for this page” an important automatic recommendation rather than forcing every page through a compression strategy.
>
> ## 5. Updated corpus files
>
> I've created and checked the revised corpus package.
>
> Download audited PDF corpus package
>
> 26 KB · Manifests, audit, dataset references, validator and photo-to-PDF builder
>
> # 23
>
> Primary PDF candidates
>
> # 9
>
> Reserve candidates
>
> # 8
>
> External benchmark sources
>
> Curated PDF manifest
>
> New image dataset sources
>
> Full audit and missing-class report
>
> Photographs-to-PDF builder
>
> The builder has been locally tested with a three-page JPEG sample: it produced a readable PDF with JPEG image streams and a provenance index containing source hashes.
>
> Still outstanding: downloading the actual public source files, measuring the real byte sizes and assembling the hard-photo benchmark PDFs. This environment couldn't retrieve those remote files, so I haven't presented the new research datasets as already-built PDF samples.
>
> My next priority would be a focused 12–16-page extreme-lighting test PDF using selected DocShadow-SD7K examples, followed by a SmartDoc handheld-photo PDF. Those two would probably reveal more about the quality of your future thresholding interface than another dozen clean government documents.

## 39 — GitHub repository migration (verbatim, 2026-10-09)
> I called my github repo, pdf-minimalist, I should already have ssh to github working locally, can you migrate and sync to github? There is only a placeholder readme there, everything can be replaced, but double check to make sure you have the correct repo.

## 40 — product and stub rename (verbatim, 2026-10-09)
> change the various names and stubs that has pdf-reducer, to pdf-minimalist.

## 41 — stale local label (verbatim, 2026-10-09)
> also, why does it say local? Ref: pdf-reducer (local)

## 42 — startup commit scope (verbatim, 2026-10-09)
> push everything together, it doesn't matter for now, this is just a startup.

## 43 — per-filter progress (verbatim, 2026-10-10)
> the progress bar is supposed to be for EACH filter.

## 44 — process-once cache (verbatim, 2026-10-10)
> when I was clicking on a filter preview, it seemed to be restarting it processing, but that is incorrect, it should be processed once and only reprocessed if there is a change of the file or change in the filter specifications.

## 45 — full-page minis + process exit (verbatim, 2026-10-10)
> Previews are truncated half page or something, when they should should the exact preview seen in the preview window, this was my previous design intent and ruling and you keep failing this.  Is it recorded?  Aso, why did the process close by itself??

## 46 — strip caption style (verbatim, 2026-10-10)
> Also, make the thumbnail preview box clear and the filter and size below it in smaller characters and aso clearly divided

## 47 — scroll reprocessing (verbatim, 2026-10-10)
> again, why is there reprocessing when I scroll????

## 48 — thumbnail meaning, clarified (verbatim, 2026-10-10)
> Still wrong! Thumbnails should be a mini version of exactly the current view of the larger window.  Why is this not clear?  If the original and preview windows (always synced view) show three pages wide and 4 pages high with the last page have cut, each preview shows exactly that from it's own filter view (internal, no shown, file preprocessed in bg at the start or from the latest change).  This seems simple and exacly derived from my previous rulings.

## 49 — open dialog with previews (verbatim, 2026-10-10)
> can we have an open file window that shows previews of the pdf files?  Does that require a custom open file control?

## 50 — drop the navigator (verbatim, 2026-10-10)
> the navigator section is useless, the original window is the navigator for now.

## 51 — preview-first priority (verbatim, 2026-10-10)
> WHen I open a new file, the right preview is the last to be updated, it should be always the first filter to be processed, ahead of all other priorities.  First open, it would be the first priority filter, but after, it would be whatever filter the user has selected, right?

## 52 — keyboard zoom (verbatim, 2026-10-10)
> what is the modern standard keypress for zoom in and zoom out, I tried and nothing worked.

## 53 — algorithm + size honesty (verbatim, 2026-10-10)
> why don't I see the image algorithm?  is that imposed?  It should still be shown in the filter details.  And is the size based on saving with this format?  And why estimated?  You should know the exact size of the file once processing is completed, no?

## 54 — details on the right (verbatim, 2026-10-10)
> filter details left side should have it, that is what I meant, this is obvious....
> sorry, right side

## Corrections log (outside the quotes, for the record)
- "JDIC2" → designer confirmed: JBIG2.
- "jpg XL" → dropped per designer ("lok, no jxl"): JXL can't be embedded in PDFs today.
- "optmized" → optimized. "targetting" → targeting. "remeber" → remember. "lok" → ok. "alot" → a lot.
  (Originals above untouched.)
