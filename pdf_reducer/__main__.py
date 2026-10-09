"""Qt entry point: python -m pdf_reducer [input.pdf] [--debug]"""
import os

# Single-thread numerical backends FIRST (before numpy/BLAS load): background
# worker threads abort under BLAS thread-pool load in constrained environments.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse

from .ui_qt.app import main, setup_logging


def cli(argv=None):
    ap = argparse.ArgumentParser(prog="pdf_reducer")
    ap.add_argument("pdf", nargs="?", default=None)
    ap.add_argument("--debug", action="store_true",
                    help="verbose stdout diagnostics for run-and-review")
    a = ap.parse_args(argv)
    setup_logging(a.debug)
    main(a.pdf, a.debug)


if __name__ == "__main__":
    cli()
