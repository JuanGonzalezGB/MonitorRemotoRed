"""
model/config.py — carga y persistencia de config.json
"""
import json
import os
import sys

DEFAULT = {
    "subnet": "192.168.0.0/24",
    "scan_interval": 7,
    "ping_warn_ms": 20,
    "devices": {}
}


def _config_path() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config.json")


class Config:
    def __init__(self):
        self.path = _config_path()
        self._data: dict = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            self._data = dict(DEFAULT)
            self._save()
            return
        try:
            with open(self.path) as f:
                self._data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[config] Error en config.json: {e}")
            self._data = dict(DEFAULT)

    def _save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self._data, f, indent=4)
        except Exception as e:
            print(f"[config] Error guardando: {e}")

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def subnet(self) -> str:
        return self._data.get("subnet", DEFAULT["subnet"])

    @subnet.setter
    def subnet(self, value: str):
        if "/" not in value:
            value += "/24"
        self._data["subnet"] = value
        self._save()

    @property
    def scan_interval(self) -> int:
        return self._data.get("scan_interval", DEFAULT["scan_interval"])

    @property
    def ping_warn_ms(self) -> int:
        return self._data.get("ping_warn_ms", DEFAULT["ping_warn_ms"])

    @property
    def devices(self) -> dict:
        return self._data.get("devices", {})

    def device_name(self, mac: str) -> str | None:
        return self.devices.get(mac, {}).get("name")

    def set_device_name(self, mac: str, name: str):
        devs = self._data.setdefault("devices", {})
        devs.setdefault(mac, {})["name"] = name
        self._save()
