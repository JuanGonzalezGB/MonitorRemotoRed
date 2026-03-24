"""
parser.py — llama al script bash y retorna lista de dispositivos
"""
import subprocess
import json
import os

SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_network.sh")


def scan(subnet: str = "192.168.1.0/24") -> list[dict]:
    """
    Ejecuta scan_network.sh y retorna lista de dicts:
    [{"ip": str, "mac": str, "vendor": str, "ping_ms": float | None}, ...]
    """
    try:
        result = subprocess.run(
            ["bash", SCRIPT_PATH, subnet],
            capture_output=True,
            text=True,
            timeout=45
        )
        raw = result.stdout.strip()
        if not raw:
            return []
        devices = json.loads(raw)
        return devices
    except subprocess.TimeoutExpired:
        print("[parser] Timeout al escanear la red")
        return []
    except json.JSONDecodeError as e:
        print(f"[parser] Error parseando JSON: {e}")
        print(f"[parser] stdout fue: {result.stdout[:200]}")
        return []
    except Exception as e:
        print(f"[parser] Error inesperado: {e}")
        return []


if __name__ == "__main__":
    # Test rápido: python3 parser.py
    import sys
    subnet = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.0/24"
    devices = scan(subnet)
    print(json.dumps(devices, indent=2))
