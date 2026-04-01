"""
main.py — punto de entrada
- Dispositivos en tiempo real: lee scanner.scans via repository (collector los escribe)
- Nombres de dispositivos:     lee/escribe scanner.dispositivos via Config
"""
import sys
from modelo.config import Config
from modelo.bandwidth import BandwidthMonitor
from controlador.network import preflight
import controlador.repository as repo
from vista.dashboard import Dashboard
from estilo.estiloFactory import EstiloFactory
from rpicore.config import REFRESH_MS


def main():
    if not preflight():
        sys.exit(1)

    config = Config()
    bw     = BandwidthMonitor()
    estilo = EstiloFactory.definirEstilo(config.theme)

    def on_rename(mac: str, name: str):
        config.set_device_name(mac, name)  # Config escribe en scanner.dispositivos

    def on_settings_change(subnet: str, interval: int, mongo: dict):
        config.subnet = subnet
        config.scan_interval = interval
        config.mongo = mongo               # reconecta Mongo si cambian credenciales

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
            app.after(REFRESH_MS, poll_mongo)

    bw.start()
    app.after(REFRESH_MS, poll_mongo)
    app.mainloop()
    bw.stop()


if __name__ == "__main__":
    main()