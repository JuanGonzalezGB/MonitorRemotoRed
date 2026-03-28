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


def _sudo_configured(arp_path: str) -> bool:
    result = subprocess.run(
        ["sudo", "-n", arp_path, "--help"],
        capture_output=True
    )
    return result.returncode == 0


def _setup_sudoers(arp_path: str) -> bool:
    user = os.environ.get("SUDO_USER") or os.environ.get("USER") or os.getlogin()
    rule = f"{user} ALL=(ALL) NOPASSWD: {arp_path}\n"
    sudoers_file = "/etc/sudoers.d/net_monitor"

    print("Primera ejecución: configurando permisos para arp-scan...")
    print(f"  Regla: {rule.strip()}")
    print("  (Ingresá tu contraseña de sudo — solo esta vez)\n")

    result = subprocess.run(
        ["sudo", "tee", sudoers_file],
        input=rule.encode(), capture_output=True
    )
    if result.returncode != 0:
        print(f"[network] Error escribiendo sudoers: {result.stderr.decode()}")
        return False

    subprocess.run(["sudo", "chmod", "440", sudoers_file], check=True)
    verify = subprocess.run(
        ["sudo", "visudo", "-c", "-f", sudoers_file],
        capture_output=True
    )
    if verify.returncode != 0:
        subprocess.run(["sudo", "rm", sudoers_file])
        return False

    print("Permisos configurados. No se volverá a pedir.\n")
    return True


def _preflight_linux() -> bool:
    arp_path = _find_arp_scan()
    if not arp_path:
        print("ERROR: arp-scan no está instalado.")
        print("  Instalalo con: sudo apt install arp-scan")
        return False
    if not _sudo_configured(arp_path):
        ok = _setup_sudoers(arp_path)
        if not ok or not _sudo_configured(arp_path):
            print("ERROR: no se pudo configurar sudo.")
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
