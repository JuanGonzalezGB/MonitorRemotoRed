"""
main.py — punto de entrada, conecta modelo, controlador y vista
"""
import sys
from modelo.config import Config
from modelo.state_cache import StateCache
from modelo.bandwidth import BandwidthMonitor
from controlador.network import preflight
from controlador.scanner import ScannerController
from vista.dashboard import Dashboard


def main():
    #if not preflight():
     #   sys.exit(1)

    config = Config()
    cache  = StateCache()
    bw     = BandwidthMonitor()

    # Vista — se crea antes del scanner para poder llamar .after()
    app = Dashboard(
        config=config,
        bw=bw,
        on_force_scan=lambda: scanner.force_scan(),
        on_settings_change=lambda s, i, m: _on_settings_change(s, i, m),
        on_rename=lambda mac, name: config.set_device_name(mac, name),
    )

    def _on_scan_result(devices):
        cache.update(devices, config)
        app.after(0, lambda d=devices: _refresh(d))

    def _refresh(devices):
        for d in devices:
            app.update_device(d)
        app.update_counts(devices)
        app.set_scanning(False)

    def _on_settings_change(subnet: str, interval: int, mongo: dict):
        config.subnet = subnet
        config.scan_interval = interval
        config.mongo = mongo
        scanner.interval = interval
        scanner.force_scan()

    scanner = ScannerController(
        get_subnet=lambda: config.subnet,
        interval=config.scan_interval,
        on_result=_on_scan_result,
    )

    # Notificar estado de scan a la vista
    original_do_scan = scanner._do_scan
    def _wrapped_scan():
        app.after(0, lambda: app.set_scanning(True))
        original_do_scan()
    scanner._do_scan = _wrapped_scan

    bw.start()
    scanner.start()
    app.mainloop()
    bw.stop()
    scanner.stop()


if __name__ == "__main__":
    main()
