import numpy as np
from pdf_reducer.core import threshold as T


def test_simple_gimp_equivalent():
    gray = np.array([[0, 127, 255]], dtype=np.uint8)
    out = T.simple(gray, 127)
    assert out.tolist() == [[0, 0, 255]]


def test_otsu_bimodal():
    gray = np.zeros((20, 20), dtype=np.uint8)
    gray[:, 10:] = 200
    t = T.otsu_threshold(gray)
    assert 0 <= t <= 200
    out = T.otsu(gray)
    assert out.min() == 0 and out.max() == 255
