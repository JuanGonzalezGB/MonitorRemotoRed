"""
controller/scanner.py — escaneo de red multiplataforma
- Linux: scan_network.sh (arp-scan + ping)
- Windows: python-nmap
"""
import os
import sys
import threading
import time
from typing import Callable

from model.device import Device


# ── Backend Linux ─────────────────────────────────────────────────────────────

def _script_path() -> str:
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "scan_network.sh")


def _scan_linux(subnet: str) -> list[Device]:
    import subprocess
    import json
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
    except Exception as e:
        print(f"[scanner] Error Linux: {e}")
        return []


# ── Backend Windows ───────────────────────────────────────────────────────────

def _scan_windows(subnet: str) -> list[Device]:
    try:
        import nmap
        import socket
    except ImportError:
        print("[scanner] python-nmap no instalado. Corré: pip install python-nmap")
        return []

    try:
        nm = nmap.PortScanner()
        # -sn: ping scan (no ports), -PR: ARP ping, --host-timeout limita tiempo por host
        nm.scan(hosts=subnet, arguments="-sn -PR --host-timeout 2s")

        devices = []
        for host in nm.all_hosts():
            try:
                info = nm[host]
                state = info.state()
                if state != "up":
                    continue

                mac = ""
                vendor = ""
                if "addresses" in info:
                    mac = info["addresses"].get("mac", "").lower()
                if "vendor" in info and mac:
                    vendor = list(info["vendor"].values())[0] if info["vendor"] else ""

                # Ping para obtener latencia
                ping_ms = _ping_windows(host)

                if not mac:
                    # Intentar obtener MAC via ARP cache
                    mac = _arp_cache_windows(host)

                if mac:
                    devices.append(Device(
                        ip=host,
                        mac=mac,
                        vendor=vendor,
                        ping_ms=ping_ms
                    ))
            except Exception as e:
                print(f"[scanner] Error procesando {host}: {e}")

        return devices
    except Exception as e:
        print(f"[scanner] Error nmap: {e}")
        return []


def _ping_windows(ip: str) -> float | None:
    import subprocess
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip],
            capture_output=True, text=True, timeout=3
        )
        for line in result.stdout.split("\n"):
            if "tiempo" in line.lower() or "time" in line.lower():
                import re
                m = re.search(r"[=<](\d+)ms", line)
                if m:
                    return float(m.group(1))
    except Exception:
        pass
    return None


def _arp_cache_windows(ip: str) -> str:
    import subprocess
    import re
    try:
        result = subprocess.run(
            ["arp", "-a", ip],
            capture_output=True, text=True, timeout=3
        )
        m = re.search(r"([0-9a-f]{2}[:-]){5}[0-9a-f]{2}", result.stdout, re.IGNORECASE)
        if m:
            return m.group(0).replace("-", ":").lower()
    except Exception:
        pass
    return ""


# ── Función pública de scan ───────────────────────────────────────────────────

def run_scan(subnet: str) -> list[Device]:
    if sys.platform == "win32":
        return _scan_windows(subnet)
    return _scan_linux(subnet)


# ── Controlador ───────────────────────────────────────────────────────────────

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

    @property
    def interval(self) -> int:
        return self._interval

    @interval.setter
    def interval(self, value: int):
        self._interval = max(1, value)

    def _do_scan(self):
        if self._scanning:
            return
        self._scanning = True
        try:
            devices = run_scan(self._get_subnet())
            self._on_result(devices)
        finally:
            self._scanning = False

    def _loop(self):
        while self._running:
            self._do_scan()
            time.sleep(self._interval)
