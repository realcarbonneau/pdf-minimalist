#!/bin/bash
# Full test suite for the designer (ruling §59: run EVERY time before ship).
# Usage: ./test.sh
# Runs the whole pytest suite (headless + offscreen Qt) and fails loudly.
set -e
cd "$(dirname "$0")"
./.venv/bin/python -m pytest tests/ -q
echo "FULL SUITE GREEN"
