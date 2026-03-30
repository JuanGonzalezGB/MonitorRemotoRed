"""
vista/dashboard.py — ventana principal del dashboard
"""
import tkinter as tk
from datetime import datetime
from typing import Callable

from modelo.device import Device
from modelo.config import Config
from modelo.bandwidth import BandwidthMonitor
from controlador.network import get_local_ip
from controlador.controladorTemas import etiquetar, ROL_BG, ROL_BG2, ROL_CYAN, ROL_MUTED, ROL_BLUE, ROL_BOTON
from vista.dialogs import RenameDialog
from vista.settings_dialog import SettingsDialog
from vista.speed_panel import SpeedPanel
from vista.selectema import ThemeSelector
from vista.gui_dictionary import FORMATS
from estilo.estiloFactory import EstiloFactory

F_TITLE  = FORMATS["F_TITLE"]
F_NORMAL = FORMATS["F_NORMAL"]
F_SMALL  = FORMATS["F_SMALL"]
COL_NAME   = FORMATS["COL_NAME"]
COL_IP     = FORMATS["COL_IP"]
COL_VENDOR = FORMATS["COL_VENDOR"]
COL_PING   = FORMATS["COL_PING"]


class Dashboard(tk.Tk):
    def __init__(self, estilo, config: Config, bw: BandwidthMonitor,
                 on_force_scan: Callable,
                 on_settings_change: Callable[[str, int, dict], None],
                 on_rename: Callable[[str, str], None]):
        super().__init__()
        self.estilo = estilo
        self.config = config
        self.bw = bw
        self.on_force_scan = on_force_scan
        self.on_settings_change = on_settings_change
        self.on_rename = on_rename

        self.rows: dict[str, dict] = {}
        self._show_mac: dict[str, bool] = {}
        self._local_ip = get_local_ip()

        self.title("Net Monitor")
        self.geometry("480x280")
        self.resizable(False, True)
        self.maxsize(480, 300)
        self.configure(bg=self.estilo.bg)
        self.overrideredirect(False)

        self._build_ui()
        self._tick_clock()

    def _build_ui(self):
        self.hdr = tk.Frame(self, bg=self.estilo.bg)
        etiquetar(self.hdr, ROL_BG)
        self.hdr.pack(fill="x", padx=8, pady=(6, 0))

        self.lbl_title = tk.Label(self.hdr, text="NET MONITOR",
                                  bg=self.estilo.bg, fg=self.estilo.cyan, font=F_TITLE)
        etiquetar(self.lbl_title, ROL_BG, ROL_CYAN)
        self.lbl_title.pack(side="left")

        self.btn_settings = tk.Button(self.hdr, text="⚙",
                  bg=self.estilo.bg, fg=self.estilo.muted,
                  font=("monospace", 11), relief="flat", bd=0, cursor="hand2",
                  activebackground=self.estilo.bg, activeforeground=self.estilo.cyan,
                  command=self._open_settings)
        etiquetar(self.btn_settings, ROL_BG, ROL_MUTED)
        self.btn_settings.pack(side="left", padx=(6, 0))

        self.btn_speed = tk.Button(self.hdr, text="↑↓",
                  bg=self.estilo.bg, fg=self.estilo.muted,
                  font=("monospace", 11), relief="flat", bd=0, cursor="hand2",
                  activebackground=self.estilo.bg, activeforeground=self.estilo.cyan,
                  command=self._open_host_speed)
        etiquetar(self.btn_speed, ROL_BG, ROL_MUTED)
        self.btn_speed.pack(side="left", padx=(4, 0))

        self.btn_theme = tk.Button(self.hdr, text="🎨",
                  bg=self.estilo.bg, fg=self.estilo.muted,
                  font=("monospace", 11), relief="flat", bd=0, cursor="hand2",
                  activebackground=self.estilo.bg, activeforeground=self.estilo.cyan,
                  command=self._open_theme)
        etiquetar(self.btn_theme, ROL_BG, ROL_MUTED)
        self.btn_theme.pack(side="left", padx=(4, 0))

        self.lbl_time = tk.Label(self.hdr, text="",
                                 bg=self.estilo.bg, fg=self.estilo.muted, font=F_SMALL)
        etiquetar(self.lbl_time, ROL_BG, ROL_MUTED)
        self.lbl_time.pack(side="right")

        self.lbl_counts = tk.Label(self.hdr, text="escaneando...",
                                   bg=self.estilo.bg, fg=self.estilo.muted, font=F_SMALL)
        etiquetar(self.lbl_counts, ROL_BG, ROL_MUTED)
        self.lbl_counts.pack(side="right", padx=12)

        sep1 = tk.Frame(self, bg=self.estilo.border, height=1)
        sep1._bg_rol = "border"
        sep1.pack(fill="x", padx=8, pady=(3, 0))

        col_hdr = tk.Frame(self, bg=self.estilo.bg)
        etiquetar(col_hdr, ROL_BG)
        col_hdr.pack(fill="x", padx=8, pady=(2, 0))
        for txt, w, anchor in [
            ("", 2, "w"), ("nombre", COL_NAME, "w"),
            ("ip / mac", COL_IP, "w"), ("vendor", COL_VENDOR, "w"),
            ("ping", COL_PING, "e")
        ]:
            lbl = tk.Label(col_hdr, text=txt, bg=self.estilo.bg, fg=self.estilo.muted,
                           font=F_SMALL, width=w, anchor=anchor)
            etiquetar(lbl, ROL_BG, ROL_MUTED)
            lbl.pack(side="left", padx=1)

        sep2 = tk.Frame(self, bg=self.estilo.border, height=1)
        sep2._bg_rol = "border"
        sep2.pack(fill="x", padx=8, pady=(1, 0))

        self.list_frame = tk.Frame(self, bg=self.estilo.bg)
        etiquetar(self.list_frame, ROL_BG)
        self.list_frame.pack(fill="both", expand=True, padx=8)

        sep3 = tk.Frame(self, bg=self.estilo.border, height=1)
        sep3._bg_rol = "border"
        sep3.pack(fill="x", padx=8, pady=(0, 2))

        ftr = tk.Frame(self, bg=self.estilo.bg)
        etiquetar(ftr, ROL_BG)
        ftr.pack(fill="x", padx=8, pady=(0, 4))

        self.lbl_last = tk.Label(ftr, text="Esperando scan...",
                                 bg=self.estilo.bg, fg=self.estilo.muted, font=F_SMALL)
        etiquetar(self.lbl_last, ROL_BG, ROL_MUTED)
        self.lbl_last.pack(side="left")

        self.lbl_subnet = tk.Label(ftr, text=self.config.subnet,
                                   bg=self.estilo.bg, fg=self.estilo.muted, font=F_SMALL)
        etiquetar(self.lbl_subnet, ROL_BG, ROL_MUTED)
        self.lbl_subnet.pack(side="left", padx=8)

        self.btn_scan = tk.Button(ftr, text="Scan",
                                  bg=self.estilo.boton, fg=self.estilo.cyan,
                                  font=F_SMALL, relief="flat", bd=0, padx=6,
                                  command=self.on_force_scan)
        etiquetar(self.btn_scan, ROL_BOTON, ROL_CYAN)
        self.btn_scan.pack(side="right")

    def refresh_ui(self, devices: list[Device]):
        incoming = {d.mac: d for d in devices}

        # actualizar/crear
        for device in devices:
            self.update_device(device)

        # marcar offline + limpiar estado visual REAL
        for mac in list(self.rows.keys()):
            if mac not in incoming:
                row = self.rows[mac]

                row["dot"].config(fg=self.estilo.red)
                row["ping"].config(text="---", fg=self.estilo.red)

                # IMPORTANTÍSIMO: desactivar interacción
                row["ping"].unbind("<Button-1>")
                row["ping"].config(cursor="")
    # ── Rows ──────────────────────────────────────────────────────────────────

    def _make_row(self, mac: str):
        estilo = self.estilo
        frame = tk.Frame(self.list_frame, bg=estilo.bg2, pady=2)
        etiquetar(frame, ROL_BG2)
        frame.pack(fill="x", pady=1)

        dot = tk.Label(frame, text="●", bg=estilo.bg2, fg=estilo.muted,
                       font=F_SMALL, width=2)
        etiquetar(dot, ROL_BG2, ROL_MUTED)

        name = tk.Label(frame, text="", bg=estilo.bg2, fg=estilo.cyan,
                        font=F_NORMAL, width=COL_NAME, anchor="w", cursor="hand2")
        etiquetar(name, ROL_BG2, ROL_CYAN)

        lbl_ip = tk.Label(frame, text="", bg=estilo.bg2, fg=estilo.blue,
                          font=F_SMALL, width=COL_IP, anchor="w", cursor="hand2")
        etiquetar(lbl_ip, ROL_BG2, ROL_BLUE)

        vendor = tk.Label(frame, text="", bg=estilo.bg2, fg=estilo.muted,
                          font=F_SMALL, width=COL_VENDOR, anchor="w")
        etiquetar(vendor, ROL_BG2, ROL_MUTED)

        ping = tk.Label(frame, text="---", bg=estilo.bg2, fg=estilo.muted,
                        font=F_NORMAL, width=COL_PING, anchor="e")
        etiquetar(ping, ROL_BG2, ROL_MUTED)

        for w in (dot, name, lbl_ip, vendor, ping):
            w.pack(side="left", padx=1)

        name.bind("<Button-1>", lambda e, m=mac: self._open_rename(m))
        lbl_ip.bind("<Button-1>", lambda e, m=mac: self._toggle_ip_mac(m))

        self._show_mac[mac] = False
        self.rows[mac] = {"frame": frame, "dot": dot, "name": name,
                          "lbl_ip": lbl_ip, "vendor": vendor,
                          "ping": ping, "ip": ""}

    def update_device(self, device: Device):
        mac = device.mac
        if mac not in self.rows:
            self._make_row(mac)

        row = self.rows[mac]
        row["ip"] = device.ip

        label = self.config.device_name(mac) or device.ip.split(".")[-1]
        row["name"].config(text=label[:COL_NAME])
        row["vendor"].config(text=device.vendor[:COL_VENDOR])

        if not self._show_mac.get(mac, False):
            row["lbl_ip"].config(text=device.ip[:COL_IP])

        if not device.online:
            row["dot"].config(fg=self.estilo.red)
            row["ping"].config(text="---", fg=self.estilo.red)
            row["dot"]._fg_rol = "red"
            row["ping"]._fg_rol = "red"
            row["ping"].config(cursor="")
            row["ping"].unbind("<Button-1>")
        else:
            ms = int(device.ping_ms)
            color = self.estilo.orange if ms > self.config.ping_warn_ms else self.estilo.green
            rol   = "orange" if ms > self.config.ping_warn_ms else "green"
            row["dot"].config(fg=self.estilo.green)
            row["dot"]._fg_rol = "green"
            row["ping"].config(text=f"{ms}ms", fg=color)
            row["ping"]._fg_rol = rol

            if device.ip == self._local_ip:
                row["ping"].config(cursor="hand2")
                row["ping"].bind("<Button-1>", lambda e, m=mac: self._open_speed(m))
            else:
                row["ping"].config(cursor="")
                row["ping"].unbind("<Button-1>")

    def update_counts(self, devices: list[Device]):
        online  = sum(1 for d in devices if d.online)
        offline = len(devices) - online
        self.lbl_counts.config(text=f"▲{online}  ▼{offline}  total {len(devices)}")
        self.lbl_last.config(text=f"scan {datetime.now().strftime('%H:%M:%S')}")

    def set_scanning(self, scanning: bool):
        if scanning:
            self.btn_scan.config(text="...", state="disabled")
        else:
            self.btn_scan.config(text="Scan", state="normal")

    def clear_devices(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.rows.clear()
        self._show_mac.clear()

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _toggle_ip_mac(self, mac: str):
        self._show_mac[mac] = not self._show_mac.get(mac, False)
        row = self.rows[mac]
        if self._show_mac[mac]:
            row["lbl_ip"].config(text=mac[:COL_IP], fg=self.estilo.muted)
            row["lbl_ip"]._fg_rol = "muted"
        else:
            row["lbl_ip"].config(text=row["ip"][:COL_IP], fg=self.estilo.blue)
            row["lbl_ip"]._fg_rol = "blue"

    def _open_rename(self, mac: str):
        ip = self.rows[mac]["ip"]
        current = self.config.device_name(mac) or mac
        RenameDialog(self, mac, ip, current, self._handle_rename, EstiloFactory.definirEstilo(self.config.theme))

    def _handle_rename(self, mac: str, name: str):
        self.on_rename(mac, name)
        if mac in self.rows:
            self.rows[mac]["name"].config(text=name[:COL_NAME])

    def _open_speed(self, mac: str):
        ip = self.rows[mac]["ip"]
        label = self.config.device_name(mac) or ip.split(".")[-1]
        SpeedPanel(EstiloFactory.definirEstilo(self.config.theme), self, label, ip, mac, self.bw)

    def _open_host_speed(self):
        local_ip = self._local_ip or "este equipo"
        SpeedPanel(EstiloFactory.definirEstilo(self.config.theme), self, "Host", local_ip, "", self.bw)

    def _open_settings(self):
        estilo = EstiloFactory.definirEstilo(self.config.theme)
        SettingsDialog(
            self,
            current_subnet=self.config.subnet,
            current_interval=self.config.scan_interval,
            current_mongo=self.config.mongo,
            on_save=self._handle_settings_save,
            estilo=estilo
        )

    def _open_theme(self):
        ThemeSelector(self, EstiloFactory.definirEstilo(self.config.theme))

    def _handle_settings_save(self, subnet: str, interval: int, mongo: dict):
        self.lbl_subnet.config(text=subnet)
        self.clear_devices()
        self.on_settings_change(subnet, interval, mongo)

    def apply_estilo(self, estilo):
        """Actualiza self.estilo para que los próximos scans y nuevos widgets usen el tema actual."""
        self.estilo = estilo

    def _tick_clock(self):
        self.lbl_time.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick_clock)
