"""
view/dashboard.py — ventana principal del dashboard
"""
import tkinter as tk
from datetime import datetime
from typing import Callable

from modelo.device import Device
from modelo.config import Config
from modelo.bandwidth import BandwidthMonitor
from controlador.network import get_local_ip
from vista.dialogs import RenameDialog
from vista.settings_dialog import SettingsDialog
from vista.speed_panel import SpeedPanel

BG      = "#0f0f12"
BG2     = "#161620"
BORDER  = "#1e1e2a"
GREEN   = "#3ddc84"
ORANGE  = "#f0a030"
RED     = "#e05252"
CYAN    = "#7fd4c1"
BLUE    = "#7a9fd4"
MUTED   = "#4a4a5a"
WHITE   = "#e0e0e8"

F_TITLE  = ("monospace", 10, "bold")
F_NORMAL = ("monospace", 9)
F_SMALL  = ("monospace", 8)

COL_NAME   = 14
COL_IP     = 15
COL_VENDOR = 12
COL_PING   =  6


class Dashboard(tk.Tk):
    def __init__(self, config: Config, bw: BandwidthMonitor,
                 on_force_scan: Callable,
                 on_settings_change: Callable[[str, int, dict], None],
                 on_rename: Callable[[str, str], None]):
        super().__init__()
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
        self.configure(bg=BG)
        self.overrideredirect(False)

        self._build_ui()
        self._tick_clock()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=8, pady=(6, 0))
        tk.Label(hdr, text="NET MONITOR", bg=BG, fg=CYAN,
                 font=F_TITLE).pack(side="left")
        tk.Button(hdr, text="⚙", bg=BG, fg=MUTED,
                  font=("monospace", 11), relief="flat", bd=0,
                  activebackground=BG, activeforeground=CYAN, cursor="hand2",
                  command=self._open_settings).pack(side="left", padx=(6, 0))
        tk.Button(hdr, text="↑↓", bg=BG, fg=MUTED,
                  font=("monospace", 11), relief="flat", bd=0,
                  activebackground=BG, activeforeground=CYAN, cursor="hand2",
                  command=self._open_host_speed).pack(side="left", padx=(4, 0))
        self.lbl_time = tk.Label(hdr, text="", bg=BG, fg=MUTED, font=F_SMALL)
        self.lbl_time.pack(side="right")
        self.lbl_counts = tk.Label(hdr, text="escaneando...",
                                   bg=BG, fg=MUTED, font=F_SMALL)
        self.lbl_counts.pack(side="right", padx=12)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=8, pady=(3, 0))

        col_hdr = tk.Frame(self, bg=BG)
        col_hdr.pack(fill="x", padx=8, pady=(2, 0))
        for txt, w, anchor in [
            ("", 2, "w"), ("nombre", COL_NAME, "w"),
            ("ip / mac", COL_IP, "w"), ("vendor", COL_VENDOR, "w"),
            ("ping", COL_PING, "e")
        ]:
            tk.Label(col_hdr, text=txt, bg=BG, fg=MUTED,
                     font=F_SMALL, width=w, anchor=anchor).pack(side="left", padx=1)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=8, pady=(1, 0))

        self.list_frame = tk.Frame(self, bg=BG)
        self.list_frame.pack(fill="both", expand=True, padx=8)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=8, pady=(0, 2))

        ftr = tk.Frame(self, bg=BG)
        ftr.pack(fill="x", padx=8, pady=(0, 4))
        self.lbl_last = tk.Label(ftr, text="Esperando scan...",
                                 bg=BG, fg=MUTED, font=F_SMALL)
        self.lbl_last.pack(side="left")
        self.lbl_subnet = tk.Label(ftr, text=self.config.subnet,
                                   bg=BG, fg=MUTED, font=F_SMALL)
        self.lbl_subnet.pack(side="left", padx=8)
        self.btn_scan = tk.Button(ftr, text="Scan", bg="#0f2520", fg=CYAN,
                                  font=F_SMALL, relief="flat", bd=0, padx=6,
                                  command=self.on_force_scan)
        self.btn_scan.pack(side="right")

    # ── Rows ─────────────────────────────────────────────────────────────────

    def _make_row(self, mac: str):
        frame = tk.Frame(self.list_frame, bg=BG2, pady=2)
        frame.pack(fill="x", pady=1)

        dot    = tk.Label(frame, text="●", bg=BG2, fg=MUTED, font=F_SMALL, width=2)
        name   = tk.Label(frame, text="", bg=BG2, fg=CYAN, font=F_NORMAL,
                          width=COL_NAME, anchor="w", cursor="hand2")
        lbl_ip = tk.Label(frame, text="", bg=BG2, fg=BLUE, font=F_SMALL,
                          width=COL_IP, anchor="w", cursor="hand2")
        vendor = tk.Label(frame, text="", bg=BG2, fg=MUTED, font=F_SMALL,
                          width=COL_VENDOR, anchor="w")
        ping   = tk.Label(frame, text="---", bg=BG2, fg=MUTED, font=F_NORMAL,
                          width=COL_PING, anchor="e")

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
            row["lbl_ip"].config(text=device.ip[:COL_IP], fg=BLUE)

        if not device.online:
            row["dot"].config(fg=RED)
            row["ping"].config(text="---", fg=RED)
            row["ping"].config(cursor="")
            row["ping"].unbind("<Button-1>")
        else:
            ms = int(device.ping_ms)
            color = ORANGE if ms > self.config.ping_warn_ms else GREEN
            row["dot"].config(fg=GREEN)
            row["ping"].config(text=f"{ms}ms", fg=color)

            # Speed panel solo en el host
            if device.ip == self._local_ip:
                row["ping"].config(cursor="hand2")
                row["ping"].bind("<Button-1>",
                                 lambda e, m=mac: self._open_speed(m))
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
            row["lbl_ip"].config(text=mac[:COL_IP], fg=MUTED)
        else:
            row["lbl_ip"].config(text=row["ip"][:COL_IP], fg=BLUE)

    def _open_rename(self, mac: str):
        ip = self.rows[mac]["ip"]
        current = self.config.device_name(mac) or mac
        RenameDialog(self, mac, ip, current, self._handle_rename)

    def _handle_rename(self, mac: str, name: str):
        self.on_rename(mac, name)
        if mac in self.rows:
            self.rows[mac]["name"].config(text=name[:COL_NAME])

    def _open_speed(self, mac: str):
        ip = self.rows[mac]["ip"]
        label = self.config.device_name(mac) or ip.split(".")[-1]
        SpeedPanel(self, label, ip, mac, self.bw)

    def _open_host_speed(self):
        from vista.speed_panel import SpeedPanel
        local_ip = self._local_ip or "este equipo"
        SpeedPanel(self, "Host", local_ip, "", self.bw)

    def _open_settings(self):
        SettingsDialog(
            self,
            current_subnet=self.config.subnet,
            current_interval=self.config.scan_interval,
            current_mongo=self.config.mongo,
            on_save=self._handle_settings_save
        )

    def _handle_settings_save(self, subnet: str, interval: int, mongo: dict):
        self.lbl_subnet.config(text=subnet)
        self.clear_devices()
        self.on_settings_change(subnet, interval, mongo)

    def _tick_clock(self):
        self.lbl_time.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick_clock)
