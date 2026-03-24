"""
state_cache.py — guarda historial de pings y estados por dispositivo
"""
from datetime import datetime


class StateCache:
    def __init__(self, max_samples: int = 60):
        self.max_samples = max_samples
        self.history: dict[str, list] = {}   # ip -> [ping_ms, ...]
        self.last_seen: dict[str, datetime] = {}
        self.first_seen: dict[str, datetime] = {}
        self.current: dict[str, dict] = {}   # ip -> último device dict

    def update(self, devices: list[dict]):
        now = datetime.now()
        for d in devices:
            ip = d["ip"]
            self.current[ip] = d
            self.last_seen[ip] = now
            if ip not in self.first_seen:
                self.first_seen[ip] = now

            samples = self.history.setdefault(ip, [])
            samples.append(d.get("ping_ms"))
            if len(samples) > self.max_samples:
                samples.pop(0)

    def avg_ping(self, ip: str) -> float | None:
        samples = [p for p in self.history.get(ip, []) if p is not None]
        if not samples:
            return None
        return round(sum(samples) / len(samples), 1)

    def is_online(self, ip: str) -> bool:
        d = self.current.get(ip)
        return d is not None and d.get("ping_ms") is not None

    def uptime_pct(self, ip: str) -> float:
        samples = self.history.get(ip, [])
        if not samples:
            return 0.0
        online = sum(1 for p in samples if p is not None)
        return round(online / len(samples) * 100, 1)
