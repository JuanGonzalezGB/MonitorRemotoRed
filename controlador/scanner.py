"""
controller/scanner.py — ejecuta el scan y notifica a la vista via callback
(DEBUG VERSION)
"""
import subprocess
import json
import os
import sys
import threading
import time
import platform
from typing import Callable

from modelo.device import Device


def _script_path() -> str:
    # Soporte PyInstaller
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        print(f"[scanner] Running in PyInstaller bundle")
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"[scanner] Running in dev mode")

    print(f"[scanner] Base path: {base}")

    # Elegir script según OS
    if platform.system() == "Windows":
        path = os.path.join(base, "scan_network.ps1")
    else:
        path = os.path.join(base, "scan_network.sh")

    print(f"[scanner] Script path: {path}")
    print(f"[scanner] Script exists: {os.path.exists(path)}")

    return path


def run_scan(subnet: str) -> list[Device]:
    print(f"\n[scanner] ===== RUN SCAN =====")
    print(f"[scanner] Subnet: {subnet}")
    print(f"[scanner] OS: {platform.system()}")

    script = _script_path()

    try:
        # Elegir comando según OS
        if platform.system() == "Windows":
            cmd = [
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-NoProfile",
                "-File", script,
                subnet
            ]
        else:
            cmd = ["bash", script, subnet]

        print(f"[scanner] Command: {' '.join(cmd)}")

        start_time = time.time()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=45
        )

        duration = time.time() - start_time

        print(f"[scanner] Return code: {result.returncode}")
        print(f"[scanner] Duration: {duration:.2f}s")

        print(f"\n[scanner] STDOUT:\n{result.stdout}")
        print(f"\n[scanner] STDERR:\n{result.stderr}")

        raw = result.stdout.strip()

        print(f"[scanner] RAW length: {len(raw)}")

        if not raw:
            print("[scanner] ❌ Empty output")
            return []

        try:
            data = json.loads(raw)
        except Exception as e:
            print(f"[scanner] ❌ JSON parse failed")
            print(f"[scanner] RAW OUTPUT:\n{raw}")
            raise e

        devices = [
            Device(
                ip=d["ip"],
                mac=d["mac"],
                vendor=d.get("vendor", ""),
                ping_ms=d.get("ping_ms")
            )
            for d in data if "ip" in d and "mac" in d
        ]

        print(f"[scanner] ✅ Devices found: {len(devices)}")

        return devices

    except subprocess.TimeoutExpired:
        print("[scanner] ❌ TIMEOUT (script took too long)")
        return []

    except json.JSONDecodeError as e:
        print(f"[scanner] ❌ JSON error: {e}")
        print(f"[scanner] RAW OUTPUT:\n{raw}")
        return []

    except Exception as e:
        print(f"[scanner] ❌ Error: {e}")
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
        print("[scanner] Controller started")
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        print("[scanner] Controller stopped")
        self._running = False

    def force_scan(self):
        print("[scanner] Force scan triggered")
        threading.Thread(target=self._do_scan, daemon=True).start()

    @property
    def scanning(self) -> bool:
        return self._scanning

    @property
    def interval(self) -> int:
        return self._interval

    @interval.setter
    def interval(self, value: int):
        print(f"[scanner] Interval set to: {value}")
        self._interval = max(1, value)

    def _do_scan(self):
        if self._scanning:
            print("[scanner] Scan already running, skipping...")
            return

        print("[scanner] Starting scan...")
        self._scanning = True

        try:
            devices = run_scan(self._get_subnet())
            print(f"[scanner] Sending {len(devices)} devices to callback")
            self._on_result(devices)
        finally:
            self._scanning = False
            print("[scanner] Scan finished")

    def _loop(self):
        print("[scanner] Entering loop")
        while self._running:
            self._do_scan()
            print(f"[scanner] Sleeping {self._interval}s...\n")
            time.sleep(self._interval)