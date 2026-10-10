# pdf-minimalist

Qt/PySide6 + PyMuPDF PDF optimizer. See `docs/00_OVERVIEW.md`.

## Run (all Python deps local in `./.venv`)
```bash
./setup_local.sh
./test.sh              # FULL suite (ruling §59: green before every ship)
./run.sh [.tmp/demo.pdf] [--debug]   # UI + stdout log, tee'd to .tmp/pdf-minimalist.log
# or:
source .venv/bin/activate
python -m pdf_minimalist [input.pdf] [--debug]
```
Scratch (demos, logs, screenshots) lives in gitignored `./.tmp/`:
`tools/make_demo.py` builds `.tmp/demo.pdf`, `tools/shot.py` captures
offscreen review shots into `.tmp/shot-*.png`.

## Layout
```
pdf-minimalist/
  pdf_minimalist/     # all app source
    core/             # headless pipeline (no Qt imports)
    ui_qt/            # Qt GUI only
  tests/              # pytest suite
  tools/check_env.py  # environment diagnostic
  requirements*.txt   # pip pins (installed into .venv)
  .venv/              # virtualenv (created by setup_local.sh, git-ignored)
```

## System (apt, NOT in this dir)
See `docs/DEPENDENCIES.md` for the full local-vs-system table.
Minimum: `python3, python3-venv, jbig2, mupdf-tools, poppler-utils`.
Qt6 system libs already present on most Debian LXDE boxes; pip PySide6
bundles its own Qt inside `.venv` so it works even without them.
