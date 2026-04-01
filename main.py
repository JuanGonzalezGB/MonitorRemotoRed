"""
main.py — punto de entrada
- Dispositivos en tiempo real: lee scanner.scans via repository (collector los escribe)
- Nombres de dispositivos:     lee/escribe scanner.dispositivos via Config
"""
import re
import subprocess
import sys
from modelo.config import Config
from modelo.bandwidth import BandwidthMonitor
from controlador.network import preflight
import controlador.repository as repo
from vista.dashboard import Dashboard
from estilo.estiloFactory import EstiloFactory

_ENV_PATH = "/home/gurthbrannon/rasphole/Source/rpi-core/.env"


def _update_env_interval(seconds: int) -> None:
    try:
        with open(_ENV_PATH, "r") as f:
            content = f.read()
        content = re.sub(
            r"^SCAN_INTERVAL_S=.*$",
            f"SCAN_INTERVAL_S={seconds}",
            content,
            flags=re.MULTILINE,
        )
        with open(_ENV_PATH, "w") as f:
            f.write(content)
        print(f"[main] SCAN_INTERVAL_S={seconds} guardado en .env")
    except Exception as e:
        print(f"[main] Error editando .env: {e}")


def _restart_collector() -> None:
    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "network-collector"],
            check=True, timeout=10,
        )
        print("[main] network-collector reiniciado")
    except Exception as e:
        print(f"[main] Error reiniciando servicio: {e}")


def main():
    if not preflight():
        sys.exit(1)

    config = Config()
    bw     = BandwidthMonitor()
    estilo = EstiloFactory.definirEstilo(config.theme)

    def on_rename(mac: str, name: str):
        config.set_device_name(mac, name)

    def on_settings_change(subnet: str, interval: int, mongo: dict):
        config.subnet    = subnet
        config.scan_interval = interval  # guarda en config.json
        config.mongo     = mongo
        _update_env_interval(interval)   # guarda en .env del servicio
        _restart_collector()

    app = Dashboard(
        estilo=estilo,
        config=config,
        bw=bw,
        on_force_scan=lambda: poll_mongo(),
        on_settings_change=on_settings_change,
        on_rename=on_rename,
    )

    def poll_mongo():
        try:
            devices = repo.get_devices(config.mongo)
            app.refresh_ui(devices)
            app.update_counts(devices)
        except Exception as e:
            app.lbl_last.config(text=f"error: {e}")
        finally:
            app.after(config.scan_interval * 1000, poll_mongo)

    bw.start()
    app.after(config.scan_interval * 1000, poll_mongo)
    app.mainloop()
    bw.stop()


if __name__ == "__main__":
    main()