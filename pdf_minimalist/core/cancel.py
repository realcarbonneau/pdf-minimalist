"""Shared cancel token. Checked per page / per image for <200ms ESC response."""
import subprocess
import threading


class CancelToken:
    def __init__(self):
        self.event = threading.Event()
        self._procs: list[subprocess.Popen] = []
        self._lock = threading.Lock()

    def cancel(self):
        self.event.set()
        with self._lock:
            for p in self._procs:
                try:
                    p.kill()
                except Exception:
                    pass

    def reset(self):
        self.event.clear()

    @property
    def cancelled(self) -> bool:
        return self.event.is_set()

    def register(self, proc: subprocess.Popen):
        with self._lock:
            self._procs.append(proc)

    def unregister(self, proc: subprocess.Popen):
        with self._lock:
            if proc in self._procs:
                self._procs.remove(proc)
