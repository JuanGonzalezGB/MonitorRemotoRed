"""
bandwidth.py — velocidad del host via /proc/net/dev (sin sudo)
"""
import time
import threading


def _get_default_iface() -> str:
    try:
        with open("/proc/net/route") as f:
            for line in f:
                fields = line.strip().split()
                if len(fields) >= 2 and fields[1] == "00000000":
                    return fields[0]
    except Exception:
        pass
    return "eth0"


def _read_iface(iface: str) -> tuple[int, int] | None:
    try:
        with open("/proc/net/dev") as f:
            for line in f:
                if ":" not in line:
                    continue
                name, data = line.split(":", 1)
                if name.strip() == iface:
                    fields = data.split()
                    return int(fields[0]), int(fields[8])
    except Exception:
        pass
    return None


class BandwidthMonitor:
    HISTORY = 30

    def __init__(self):
        self._iface = _get_default_iface()
        self._lock = threading.Lock()
        self._rx_hist: list[float] = []
        self._tx_hist: list[float] = []
        self._prev: tuple[int, int] | None = None
        self._prev_time: float = 0.0
        self._running = False

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            stats = _read_iface(self._iface)
            now = time.time()
            if stats and self._prev and self._prev_time:
                dt = now - self._prev_time
                if dt > 0:
                    rx = max(0.0, (stats[0] - self._prev[0]) / dt / 1024)
                    tx = max(0.0, (stats[1] - self._prev[1]) / dt / 1024)
                    with self._lock:
                        self._rx_hist.append(rx)
                        self._tx_hist.append(tx)
                        if len(self._rx_hist) > self.HISTORY:
                            self._rx_hist.pop(0)
                        if len(self._tx_hist) > self.HISTORY:
                            self._tx_hist.pop(0)
            self._prev = stats
            self._prev_time = now
            time.sleep(1)

    def current(self) -> tuple[float, float]:
        with self._lock:
            rx = self._rx_hist[-1] if self._rx_hist else 0.0
            tx = self._tx_hist[-1] if self._tx_hist else 0.0
        return rx, tx

    def history(self) -> tuple[list[float], list[float]]:
        with self._lock:
            return list(self._rx_hist), list(self._tx_hist)
