# pdf-reducer (local)

Qt/PySide6 + PyMuPDF PDF optimizer. See `docs/00_OVERVIEW.md`.

## Run (all Python deps local in `./.venv`)
```bash
./setup_local.sh
./run.sh [.tmp/demo.pdf] [--debug]   # UI + stdout log, tee'd to .tmp/pdf-reducer.log
# or:
source .venv/bin/activate
python -m pdf_reducer [input.pdf] [--debug]
```
Scratch (demos, logs, screenshots) lives in gitignored `./.tmp/`:
`tools/make_demo.py` builds `.tmp/demo.pdf`, `tools/shot.py` captures
offscreen review shots into `.tmp/shot-*.png`.

## Layout (local = in this dir)
```
pdf-reducer/
  pdf_reducer/        # LOCAL: all app source
    core/             # headless pipeline (no Qt imports)
    ui_qt/            # Qt GUI only
  tests/              # LOCAL: pytest suite
  tools/check_env.py  # LOCAL: env diagnostic
  requirements*.txt   # LOCAL: pip pins (installed into .venv)
  .venv/              # LOCAL: virtualenv (created by setup_local.sh, git-ignored)
```

## System (apt, NOT in this dir)
See `docs/DEPENDENCIES.md` for the full local-vs-system table.
Minimum: `python3, python3-venv, jbig2, mupdf-tools, poppler-utils`.
Qt6 system libs already present on most Debian LXDE boxes; pip PySide6
bundles its own Qt inside `.venv` so it works even without them.
