import subprocess
import json
import os
import sys
import threading
import time
from typing import Callable

from modelo.device import Device


def _script_path() -> str:
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "scan_network.sh")


def run_scan(subnet: str) -> list[Device]:
    script = _script_path()
    try:
        result = subprocess.run(
            ["bash", script, subnet],
            capture_output=True, text=True, timeout=45
        )
        raw = result.stdout.strip()
        if not raw:
            return []
        data = json.loads(raw)
        return [
            Device(
                ip=d["ip"],
                mac=d["mac"],
                vendor=d.get("vendor", ""),
                ping_ms=d.get("ping_ms")
            )
            for d in data if "ip" in d and "mac" in d
        ]
    except subprocess.TimeoutExpired:
        print("[scanner] Timeout")
        return []
    except json.JSONDecodeError as e:
        print(f"[scanner] JSON error: {e}")
        return []
    except Exception as e:
        print(f"[scanner] Error: {e}")
        return []


class ScannerController:
    def __init__(self, get_subnet: Callable[[], str],
                 interval: int,
                 on_result: Callable[[list[Device]], None]):
        self._get_subnet = get_subnet
        self._interval = interval
        self._on_result = on_result
        self._scanning = False
        self._running = False

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False

    def force_scan(self):
        threading.Thread(target=self._do_scan, daemon=True).start()

    @property
    def scanning(self) -> bool:
        return self._scanning

    def _do_scan(self):
        if self._scanning:
            return
        self._scanning = True
        try:
            devices = run_scan(self._get_subnet())
            # ✅ Llamada directa al refresh UI que hace offline correctamente
            self._on_result(devices)
        finally:
            self._scanning = False

    def _loop(self):
        while self._running:
            self._do_scan()
            time.sleep(self._interval)