#!/bin/bash
# Local setup: everything Python-side stays in ./.venv (local).
# System packages (apt) stay outside the repo — see DEPENDENCIES.md.
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt
echo "OK. Run: ./.venv/bin/python -m pdf_minimalist"
