"""BW threshold strategies. Pure numpy, no OpenCV required."""
import numpy as np


def simple(gray: np.ndarray, t: int = 127) -> np.ndarray:
    """GIMP-Threshold equivalent: global cutoff (matches OpenCV THRESH_BINARY: dst = src > t)."""
    return (gray > t).astype(np.uint8) * 255


def otsu_threshold(gray: np.ndarray) -> int:
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    total = gray.size
    sum_all = np.dot(np.arange(256), hist)
    sum_b, w_b, best, thresh = 0.0, 0.0, 0.0, 127
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_all - sum_b) / w_f
        between = w_b * w_f * (m_b - m_f) ** 2
        if between > best:
            best, thresh = between, t
    return int(thresh)


def otsu(gray: np.ndarray) -> np.ndarray:
    return simple(gray, otsu_threshold(gray))


def adaptive_mean(gray: np.ndarray, block: int = 31, c: int = 10) -> np.ndarray:
    """Box-blur adaptive threshold (integral-image, no cv2)."""
    if block % 2 == 0:
        block += 1
    g = gray.astype(np.float32)
    ii = np.pad(g, 1).cumsum(0).cumsum(1)
    h, w = g.shape
    b = block // 2
    ys, xs = np.ogrid[:h, :w]
    y1 = np.clip(ys - b, 0, h - 1)
    y2 = np.clip(ys + b + 1, 0, h)
    x1 = np.clip(xs - b, 0, w - 1)
    x2 = np.clip(xs + b + 1, 0, w)
    # integral image with 1-px pad: offset by +1
    area = (y2 - y1) * (x2 - x1)
    mean = (ii[y2 + 1, x2 + 1] - ii[y1 + 1, x2 + 1] - ii[y2 + 1, x1 + 1] + ii[y1 + 1, x1 + 1]) / np.maximum(area, 1)
    return (g >= (mean - c)).astype(np.uint8) * 255


def sauvola(gray: np.ndarray, window: int = 31, k: float = 0.25, r: int = 128) -> np.ndarray:
    """Sauvola for stained/yellowed paper. Slowest, best on bad scans."""
    if window % 2 == 0:
        window += 1
    g = gray.astype(np.float32)
    ii = np.pad(g, 1).cumsum(0).cumsum(1)
    ii2 = np.pad(g * g, 1).cumsum(0).cumsum(1)
    h, w = g.shape
    b = window // 2
    ys, xs = np.ogrid[:h, :w]
    y1 = np.clip(ys - b, 0, h - 1)
    y2 = np.clip(ys + b + 1, 0, h)
    x1 = np.clip(xs - b, 0, w - 1)
    x2 = np.clip(xs + b + 1, 0, w)
    area = np.maximum((y2 - y1) * (x2 - x1), 1)
    mean = (ii[y2 + 1, x2 + 1] - ii[y1 + 1, x2 + 1] - ii[y2 + 1, x1 + 1] + ii[y1 + 1, x1 + 1]) / area
    sq = (ii2[y2 + 1, x2 + 1] - ii2[y1 + 1, x2 + 1] - ii2[y2 + 1, x1 + 1] + ii2[y1 + 1, x1 + 1]) / area
    std = np.sqrt(np.maximum(sq - mean * mean, 0))
    thresh = mean * (1 + k * (std / r - 1))
    return (g >= thresh).astype(np.uint8) * 255


STRATEGIES = {"simple": simple, "otsu": otsu, "adaptive": adaptive_mean, "sauvola": sauvola}
