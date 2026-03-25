"""
main.py — punto de entrada del dashboard de red
Primera ejecución: configura sudoers automáticamente si hace falta.
"""
import json
import os
import sys
import subprocess
import shutil

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
SUDOERS_FILE = "/etc/sudoers.d/net_monitor"


def find_arp_scan() -> str | None:
    path = shutil.which("arp-scan")
    if path:
        return path
    for p in ("/usr/sbin/arp-scan", "/usr/bin/arp-scan", "/sbin/arp-scan"):
        if os.path.isfile(p):
            return p
    return None


def sudo_is_configured(arp_path: str) -> bool:
    """Devuelve True si ya podemos correr arp-scan sin contraseña."""
    result = subprocess.run(
        ["sudo", "-n", arp_path, "--help"],
        capture_output=True
    )
    return result.returncode == 0


def setup_sudoers(arp_path: str):
    """Escribe la regla de sudoers. Pide clave de sudo una sola vez."""
    user = os.environ.get("SUDO_USER") or os.environ.get("USER") or os.getlogin()
    rule = f"{user} ALL=(ALL) NOPASSWD: {arp_path}\n"

    print("Primera ejecución: configurando permisos para arp-scan...")
    print(f"  Se escribirá: {rule.strip()}")
    print(f"  en: {SUDOERS_FILE}")
    print("  (Ingresá tu contraseña de sudo — solo esta vez)\n")

    # Escribir el archivo sudoers via sudo tee
    result = subprocess.run(
        ["sudo", "tee", SUDOERS_FILE],
        input=rule.encode(),
        capture_output=True
    )
    if result.returncode != 0:
        print("ERROR: no se pudo escribir el sudoers.")
        print(result.stderr.decode())
        sys.exit(1)

    # Asignar permisos correctos
    subprocess.run(["sudo", "chmod", "440", SUDOERS_FILE], check=True)

    # Verificar
    verify = subprocess.run(
        ["sudo", "visudo", "-c", "-f", SUDOERS_FILE],
        capture_output=True
    )
    if verify.returncode != 0:
        print("ERROR: sudoers inválido, eliminando...")
        subprocess.run(["sudo", "rm", SUDOERS_FILE])
        sys.exit(1)

    print("Permisos configurados. No se volverá a pedir.\n")


DEFAULT_CONFIG = {
    "subnet": "192.168.0.0/24",
    "scan_interval": 7,
    "ping_warn_ms": 20,
    "devices": {}
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        print(f"config.json no encontrado, creando con valores por defecto en {CONFIG_PATH}")
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        config = DEFAULT_CONFIG.copy()
        config["_path"] = CONFIG_PATH
        return config
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        config["_path"] = CONFIG_PATH
        return config
    except json.JSONDecodeError as e:
        print(f"ERROR en config.json: {e}")
        sys.exit(1)


def preflight_check():
    """Verifica dependencias y configura lo necesario antes de abrir la GUI."""
    arp_path = find_arp_scan()
    if not arp_path:
        print("ERROR: arp-scan no está instalado.")
        print("  Instalalo con: sudo apt install arp-scan")
        sys.exit(1)

    if not sudo_is_configured(arp_path):
        setup_sudoers(arp_path)

        # Verificar que quedó bien
        if not sudo_is_configured(arp_path):
            print("ERROR: no se pudo configurar sudo correctamente.")
            sys.exit(1)


if __name__ == "__main__":
    preflight_check()
    config = load_config()

    from gui import NetworkDashboard
    app = NetworkDashboard(config)
    app.mainloop()
