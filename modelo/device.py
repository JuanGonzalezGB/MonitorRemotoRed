"""
model/device.py — representación de un dispositivo de red
"""
from dataclasses import dataclass, field


@dataclass
class Device:
    ip: str
    mac: str
    vendor: str = ""
    ping_ms: float | None = None

    @property
    def online(self) -> bool:
        return self.ping_ms is not None
