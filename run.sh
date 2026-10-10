#!/bin/bash
# Local UI launcher for the designer. Stays in this dir; scratch goes to ./.tmp/.
# Usage: ./run.sh [file.pdf] [--debug]
set -e
cd "$(dirname "$0")"
mkdir -p .tmp
if [ $# -eq 0 ]; then
  set -- examples/images.pdf
fi
./.venv/bin/python -m pdf_minimalist "$@" 2>&1 | tee .tmp/pdf-minimalist.log
