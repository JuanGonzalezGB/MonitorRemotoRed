"""
state_cache.py — historial de estados indexado por MAC
"""
from datetime import datetime


class StateCache:
    def __init__(self, max_samples: int = 60):
        self.max_samples = max_samples
        self.history: dict[str, list] = {}      # mac -> [ping_ms, ...]
        self.last_seen: dict[str, datetime] = {}
        self.current: dict[str, dict] = {}       # mac -> último device dict

    def update(self, devices: list[dict]):
        now = datetime.now()
        for d in devices:
            mac = d.get("mac")
            if not mac:
                continue
            self.current[mac] = d
            self.last_seen[mac] = now
            samples = self.history.setdefault(mac, [])
            samples.append(d.get("ping_ms"))
            if len(samples) > self.max_samples:
                samples.pop(0)

    def avg_ping(self, mac: str) -> float | None:
        samples = [p for p in self.history.get(mac, []) if p is not None]
        return round(sum(samples) / len(samples), 1) if samples else None

    def uptime_pct(self, mac: str) -> float:
        samples = self.history.get(mac, [])
        if not samples:
            return 0.0
        return round(sum(1 for p in samples if p is not None) / len(samples) * 100, 1)
