# Dependencies: LOCAL (this dir) vs SYSTEM (apt / OS)

Checked on this machine (Debian 13 trixie, Python 3.13.5) on 2026-10-09.

## SYSTEM — installed via apt, shared by the OS, NOT in this repo
| Package | Status here | Why system |
|---|---|---|
| `python3, python3-venv` | present 3.13.5 | interpreter itself can't live in repo |
| `libqt6core/gui/widgets 6.8.2` | already installed | Qt C++ runtime; pip PySide6 bundles its own copy, but apt copy helps other apps |
| `jbig2` (`/usr/bin/jbig2`, libjbig2enc) | present 0.30 | best BW encoder, no pure-Python equivalent; called as subprocess |
| `jbig2dec` | present | debug/verify JBIG2 output |
| `mutool` (mupdf-tools), `libmupdf` | present | inspect/clean PDFs, fallback renderer |
| `pdfimages` (poppler-utils) | present | debug: list/extract embedded images |
| `python3-pil (pillow 11.1)`, `python3-numpy 2.2.4` | present as system dist-packages | usable without venv, but we still pin pip copies in `.venv` for reproducibility |
| fonts, libgl/egl, PCManFM (for DnD) | OS-provided | can't/shouldn't vendor |

Install missing system bits with:
```bash
sudo apt install python3-venv jbig2 mupdf-tools poppler-utils
# optional, only if you want apt-Qt bindings instead of pip:
sudo apt install python3-pyside6.qtcore python3-pyside6.qtgui python3-pyside6.qtwidgets python3-pymupdf
```

## LOCAL — in `/home/user/Downloads/pdf-reducer/`, yours to keep
| Path | What |
|---|---|
| `pdf_reducer/` | all app source (`core/` headless + `ui_qt/` GUI) |
| `tests/` | pytest suite + future fixtures in `tests/data/` |
| `tools/check_env.py` | prints system-vs-local diagnostic |
| `requirements.txt` | `pymupdf, PySide6-Essentials, Pillow, numpy` → installed into `.venv`, NOT system-wide |
| `.venv/` | local virtualenv (created by `setup_local.sh`, git-ignored) |
| `*.md` | design docs (overview, architecture, UX, test plan, this file) |

Rule: `pip install` always goes to `./.venv` (via `setup_local.sh`).
`apt install` goes to the OS. Never `sudo pip install`.
