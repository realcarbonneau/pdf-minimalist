"""pytest bootstrap: single-thread numerical backends before anything loads BLAS.

Background QThread workers abort under BLAS thread-pool load in constrained
environments (designer §37). Same guards live in pdf_reducer/__main__.py
(app entry) and tools/shot.py.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
