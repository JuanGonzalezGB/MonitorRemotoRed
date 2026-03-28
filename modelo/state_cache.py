"""
model/state_cache.py — historial de estados indexado por MAC
"""
from datetime import datetime
from .device import Device


class StateCache:
    HISTORY = 60

    def __init__(self):
        self._ping_hist: dict[str, list] = {}
        self._last_seen: dict[str, datetime] = {}
        self._current: dict[str, Device] = {}

    def update(self, devices: list[Device], config=None):
        now = datetime.now()
        for d in devices:
            if config and d.mac not in self._current:
                config.register_device(d.mac)
            self._current[d.mac] = d
            self._last_seen[d.mac] = now
            hist = self._ping_hist.setdefault(d.mac, [])
            hist.append(d.ping_ms)
            if len(hist) > self.HISTORY:
                hist.pop(0)

    def avg_ping(self, mac: str) -> float | None:
        samples = [p for p in self._ping_hist.get(mac, []) if p is not None]
        return round(sum(samples) / len(samples), 1) if samples else None

    def uptime_pct(self, mac: str) -> float:
        samples = self._ping_hist.get(mac, [])
        if not samples:
            return 0.0
        return round(sum(1 for p in samples if p is not None) / len(samples) * 100, 1)

    def all_devices(self) -> list[Device]:
        return list(self._current.values())
