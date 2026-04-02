"""
controller/network.py — preflight multiplataforma
- Linux: verifica arp-scan, configura sudoers
- Windows: verifica nmap
"""
import os
import sys
import socket
import subprocess
import shutil


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""


# ── Linux ─────────────────────────────────────────────────────────────────────

def _find_arp_scan() -> str | None:
    path = shutil.which("arp-scan")
    if path:
        return path
    for p in ("/usr/sbin/arp-scan", "/usr/bin/arp-scan", "/sbin/arp-scan"):
        if os.path.isfile(p):
            return p
    return None


def _preflight_linux() -> bool:
    arp_path = _find_arp_scan()
    if not arp_path:
        print("ERROR: arp-scan no está instalado.")
        print("  Instalalo con: sudo apt install arp-scan")
        return False

    # Verificar capabilities en lugar de sudo
    result = subprocess.run(
        ["getcap", arp_path],
        capture_output=True, text=True
    )
    if "cap_net_raw" not in result.stdout:
        print("ERROR: arp-scan no tiene las capabilities necesarias.")
        print(f"  Ejecuta: sudo setcap cap_net_raw,cap_net_admin=eip {arp_path}")
        return False

    return True


# ── Windows ───────────────────────────────────────────────────────────────────

def _preflight_windows() -> bool:
    try:
        import nmap
    except ImportError:
        print("ERROR: python-nmap no instalado.")
        print("  Instalalo con: pip install python-nmap")
        return False

    nmap_path = shutil.which("nmap")
    if not nmap_path:
        print("ERROR: nmap no encontrado en el PATH.")
        print("  Descargalo en: https://nmap.org/download.html")
        return False

    return True


# ── Pública ───────────────────────────────────────────────────────────────────

def preflight() -> bool:
    if sys.platform == "win32":
        return _preflight_windows()
    return _preflight_linux()
