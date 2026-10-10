import threading, time
from pdf_minimalist.core.cancel import CancelToken


def test_cancel_token_basic():
    tok = CancelToken()
    assert not tok.cancelled
    tok.cancel()
    assert tok.cancelled
    tok.reset()
    assert not tok.cancelled


def test_cancel_stops_loop():
    tok = CancelToken()
    seen = []

    def work():
        for i in range(50):
            if tok.cancelled:
                break
            seen.append(i)
            time.sleep(0.001)

    th = threading.Thread(target=work)
    th.start()
    time.sleep(0.005)
    tok.cancel()
    th.join()
    assert len(seen) < 50
