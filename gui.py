"""
gui.py — Dashboard de red local para Raspberry Pi con pantalla 3.5" (480x320)
Paleta oscura, fuente monospace, actualización automática en background thread.
"""
import tkinter as tk
import threading
import time
from datetime import datetime

from parser import scan
from state_cache import StateCache

# ── Colores ──────────────────────────────────────────────────────────────────
BG      = "#0f0f12"   # fondo principal
BG2     = "#161620"   # fondo filas
BORDER  = "#1e1e2a"   # líneas separadoras
GREEN   = "#3ddc84"   # online / ping ok
ORANGE  = "#f0a030"   # ping lento
RED     = "#e05252"   # offline
CYAN    = "#7fd4c1"   # título / acento
BLUE    = "#7a9fd4"   # IPs
MUTED   = "#4a4a5a"   # texto secundario
WHITE   = "#e0e0e8"   # texto principal

# ── Fuentes ──────────────────────────────────────────────────────────────────
F_TITLE  = ("monospace", 10, "bold")
F_NORMAL = ("monospace", 9)
F_SMALL  = ("monospace", 8)

# ── Columnas: (atributo_del_dict, ancho_chars, anchor) ───────────────────────
# Se definen aquí para fácil ajuste
COL_NAME   = 14
COL_IP     = 15
COL_VENDOR = 12
COL_PING   =  6


class NetworkDashboard(tk.Tk):

    def __init__(self, config: dict):
        super().__init__()
        self.config_data = config
        self.subnet       = config["subnet"]
        self.scan_interval= config["scan_interval"]
        self.ping_warn    = config["ping_warn_ms"]
        self.known        = config.get("devices", {})

        self.cache = StateCache()
        self.rows: dict[str, dict] = {}   # ip -> widgets
        self._scanning = False

        self.title("Net Monitor")
        self.geometry("480x300")
        self.resizable(False, True)
        #self.overrideredirect(True)
        self.configure(bg=BG)
        # Sin barra de título — comentar esta línea para desarrollo en desktop
        # self.overrideredirect(True)

        self._build_ui()
        self._start_scan_loop()

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=8, pady=(6, 0))

        tk.Label(hdr, text="NET MONITOR", bg=BG, fg=CYAN,
                 font=F_TITLE).pack(side="left")

        self.lbl_time = tk.Label(hdr, text="", bg=BG, fg=MUTED, font=F_SMALL)
        self.lbl_time.pack(side="right")

        self.lbl_counts = tk.Label(hdr, text="escaneando...",
                                   bg=BG, fg=MUTED, font=F_SMALL)
        self.lbl_counts.pack(side="right", padx=12)

        # ── Separador ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=8, pady=(3, 0))

        # ── Cabecera de columnas ──
        col_hdr = tk.Frame(self, bg=BG)
        col_hdr.pack(fill="x", padx=8, pady=(2, 0))
        for txt, w, anchor in [
            ("", 2, "w"), ("nombre", COL_NAME, "w"),
            ("ip", COL_IP, "w"), ("vendor", COL_VENDOR, "w"),
            ("ping", COL_PING, "e")
        ]:
            tk.Label(col_hdr, text=txt, bg=BG, fg=MUTED,
                     font=F_SMALL, width=w, anchor=anchor).pack(side="left", padx=1)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=8, pady=(1, 0))

        # ── Lista de dispositivos ──
        self.list_frame = tk.Frame(self, bg=BG)
        self.list_frame.pack(fill="both", expand=True, padx=8)

        # ── Separador footer ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=8, pady=(0, 2))

        # ── Footer ──
        ftr = tk.Frame(self, bg=BG)
        ftr.pack(fill="x", padx=8, pady=(0, 4))

        self.lbl_last = tk.Label(ftr, text="Esperando primer scan...",
                                 bg=BG, fg=MUTED, font=F_SMALL)
        self.lbl_last.pack(side="left")

        self.lbl_subnet = tk.Label(ftr, text=self.subnet,
                                   bg=BG, fg=MUTED, font=F_SMALL)
        self.lbl_subnet.pack(side="left", padx=8)

        self.btn_scan = tk.Button(
            ftr, text="Scan", bg="#0f2520", fg=CYAN,
            font=F_SMALL, relief="flat", bd=0, padx=6,
            command=self._force_scan
        )
        self.btn_scan.pack(side="right")

        self._tick_clock()

    def _make_row(self, ip: str):
        """Crea los widgets de una fila para un dispositivo."""
        frame = tk.Frame(self.list_frame, bg=BG2, pady=2)
        frame.pack(fill="x", pady=1)

        dot  = tk.Label(frame, text="●", bg=BG2, fg=MUTED,
                        font=F_SMALL, width=2)
        name = tk.Label(frame, text="", bg=BG2, fg=WHITE,
                        font=F_NORMAL, width=COL_NAME, anchor="w")
        lbl_ip = tk.Label(frame, text=ip, bg=BG2, fg=BLUE,
                          font=F_SMALL, width=COL_IP, anchor="w")
        vendor = tk.Label(frame, text="", bg=BG2, fg=MUTED,
                          font=F_SMALL, width=COL_VENDOR, anchor="w")
        ping = tk.Label(frame, text="---", bg=BG2, fg=MUTED,
                        font=F_NORMAL, width=COL_PING, anchor="e")

        for w in (dot, name, lbl_ip, vendor, ping):
            w.pack(side="left", padx=1)

        self.rows[ip] = {"frame": frame, "dot": dot,
                         "name": name, "ping": ping, "vendor": vendor}

    def _update_row(self, device: dict):
        ip = device["ip"]
        if ip not in self.rows:
            self._make_row(ip)

        row = self.rows[ip]
        info = self.known.get(ip, {})
        label = info.get("name", ip.split(".")[-1])
        vendor_str = device.get("vendor", "")[:COL_VENDOR]
        p = device.get("ping_ms")

        row["name"].config(text=label[:COL_NAME])
        row["vendor"].config(text=vendor_str)

        if p is None:
            row["dot"].config(fg=RED)
            row["ping"].config(text="---", fg=RED)
            row["frame"].config(bg=BG2)
        else:
            ms = int(p)
            color = ORANGE if ms > self.ping_warn else GREEN
            row["dot"].config(fg=GREEN)
            row["ping"].config(text=f"{ms}ms", fg=color)
            row["frame"].config(bg=BG2)

    # ── Scan ─────────────────────────────────────────────────────────────────

    def _do_scan(self):
        if self._scanning:
            return
        self._scanning = True
        self.after(0, lambda: self.btn_scan.config(text="...", state="disabled"))

        try:
            devices = scan(self.subnet)
            self.cache.update(devices)
            self.after(0, lambda d=devices: self._refresh_ui(d))
        finally:
            self._scanning = False
            self.after(0, lambda: self.btn_scan.config(text="Scan", state="normal"))

    def _refresh_ui(self, devices: list[dict]):
        online  = sum(1 for d in devices if d.get("ping_ms") is not None)
        offline = len(devices) - online
        self.lbl_counts.config(
            text=f"▲{online}  ▼{offline}  total {len(devices)}"
        )
        now_str = datetime.now().strftime("%H:%M:%S")
        self.lbl_last.config(text=f"scan {now_str}")

        for d in devices:
            self._update_row(d)

    def _force_scan(self):
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _start_scan_loop(self):
        def loop():
            while True:
                self._do_scan()
                time.sleep(self.scan_interval)
        threading.Thread(target=loop, daemon=True).start()

    # ── Reloj ─────────────────────────────────────────────────────────────────

    def _tick_clock(self):
        self.lbl_time.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick_clock)
