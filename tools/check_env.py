"""Diagnose system vs local env. Run: python3 tools/check_env.py (system) or .venv/bin/python tools/check_env.py (local)."""
import importlib.util
import shutil
import sys

print(f"python: {sys.version.split()[0]}  exe={sys.executable}")
print(f"prefix: {sys.prefix}  (project .venv if path contains pdf-minimalist/.venv)")
print()
for mod, pkg in [("fitz", "pymupdf"), ("PySide6", "PySide6-Essentials"),
                 ("PIL", "Pillow"), ("numpy", "numpy")]:
    print(f"{pkg:22} {'LOCAL-OK' if importlib.util.find_spec(mod) else 'MISSING here'}")
print()
for exe in ["jbig2", "pdfimages", "mutool"]:
    print(f"system:{exe:12} {shutil.which(exe) or 'NOT FOUND (sudo apt install jbig2 mupdf-tools poppler-utils)'}")
