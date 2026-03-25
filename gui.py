"""
gui.py — Dashboard de red local para Raspberry Pi con pantalla 3.5" (480x300)
"""
import tkinter as tk
import threading
import time
import json
from datetime import datetime

from parser import scan
from state_cache import StateCache

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


class NumpadDialog(tk.Toplevel):
    """Diálogo base con teclado numérico para ingresar IPs y subredes."""

    def __init__(self, parent, title: str, value: str, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self._build(parent, title, value)
        self.grab_set()

    def _build(self, parent, title: str, value: str):
        self.overrideredirect(True)
        self.configure(bg=BG)
        self.geometry(f"480x300+{parent.winfo_x()}+{parent.winfo_y()}")

        tk.Label(self, text=title, bg=BG, fg=CYAN,
                 font=F_SMALL).pack(pady=(8, 4))

        entry_frame = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        entry_frame.pack(padx=60, fill="x")
        self.var = tk.StringVar(value=value)
        self.entry = tk.Entry(entry_frame, textvariable=self.var,
                              bg=BG2, fg=WHITE, insertbackground=CYAN,
                              font=("monospace", 11), relief="flat", bd=3,
                              justify="center")
        self.entry.pack(fill="x")
        self.entry.focus_set()
        self.entry.icursor("end")

        # Numpad horizontal: todos en dos filas para ahorrar espacio vertical
        kb = tk.Frame(self, bg=BG)
        kb.pack(pady=(8, 0))

        keys = [
            ["1","2","3","4","5","6","7","8","9","0"],
            [".",".","/","⌫","Limpiar"],
        ]

        # Fila de dígitos
        rf1 = tk.Frame(kb, bg=BG)
        rf1.pack()
        for ch in ["1","2","3","4","5","6","7","8","9","0"]:
            tk.Button(rf1, text=ch, width=3, bg=BG2, fg=WHITE,
                      font=F_NORMAL, relief="flat", bd=0,
                      activebackground=BORDER, activeforeground=CYAN,
                      command=lambda c=ch: self._type(c)
            ).pack(side="left", padx=1, pady=2)

        # Fila especial
        rf2 = tk.Frame(kb, bg=BG)
        rf2.pack(pady=(2,0))
        for ch, fg, w, cmd in [
            (".", WHITE, 4, lambda: self._type(".")),
            ("/", WHITE, 4, lambda: self._type("/")),
            ("⌫", ORANGE, 4, self._backspace),
            ("Limpiar", MUTED, 8, lambda: self.var.set("")),
        ]:
            tk.Button(rf2, text=ch, width=w, bg=BG2, fg=fg,
                      font=F_SMALL, relief="flat", bd=0,
                      activebackground=BORDER,
                      command=cmd
            ).pack(side="left", padx=2)

        # Botones guardar/cancelar
        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(10, 0))
        tk.Button(bf, text="Cancelar", bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Guardar", bg="#0f2520", fg=CYAN,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._save).pack(side="left", padx=6)

        self.entry.bind("<Return>", lambda e: self._save())
        self.entry.bind("<Escape>", lambda e: self.destroy())

    def _type(self, ch: str):
        pos = self.entry.index("insert")
        self.var.set(self.var.get()[:pos] + ch + self.var.get()[pos:])
        self.entry.icursor(pos + 1)

    def _backspace(self):
        pos = self.entry.index("insert")
        if pos > 0:
            val = self.var.get()
            self.var.set(val[:pos-1] + val[pos:])
            self.entry.icursor(pos - 1)

    def _save(self):
        val = self.var.get().strip()
        if val:
            self.on_save(val)
        self.destroy()


class RenameDialog(tk.Toplevel):
    KEYS = [
        list("1234567890"),
        list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm-_"),
    ]

    def __init__(self, parent, mac: str, ip: str, current_name: str, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.mac = mac
        self.ip = ip
        self._uppercase = False
        self.overrideredirect(True)
        self.configure(bg=BG)
        self.geometry(f"480x300+{parent.winfo_x()}+{parent.winfo_y()}")
        self._build(current_name)
        self.grab_set()

    def _build(self, current_name: str):
        tk.Label(self, text=f"Renombrar  {self.ip}  ({self.mac})",
                 bg=BG, fg=CYAN, font=F_SMALL).pack(pady=(12, 4))

        entry_frame = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        entry_frame.pack(padx=24, fill="x")
        self.var = tk.StringVar(value=current_name)
        self.entry = tk.Entry(entry_frame, textvariable=self.var,
                              bg=BG2, fg=WHITE, insertbackground=CYAN,
                              font=("monospace", 12), relief="flat", bd=4)
        self.entry.pack(fill="x")
        self.entry.focus_set()
        self.entry.icursor("end")

        kb_frame = tk.Frame(self, bg=BG)
        kb_frame.pack(pady=(8, 0), padx=8)

        for row in self.KEYS:
            row_frame = tk.Frame(kb_frame, bg=BG)
            row_frame.pack()
            for ch in row:
                tk.Button(
                    row_frame, text=ch, width=3, bg=BG2, fg=WHITE,
                    font=F_SMALL, relief="flat", bd=0,
                    activebackground=BORDER, activeforeground=CYAN,
                    command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        special = tk.Frame(kb_frame, bg=BG)
        special.pack(pady=(2, 0))
        tk.Button(special, text="ABC", width=4, bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0,
                  command=self._toggle_case).pack(side="left", padx=1)
        tk.Button(special, text="espacio", width=8, bg=BG2, fg=WHITE,
                  font=F_SMALL, relief="flat", bd=0,
                  command=lambda: self._type(" ")).pack(side="left", padx=1)
        tk.Button(special, text="⌫", width=4, bg=BG2, fg=ORANGE,
                  font=F_SMALL, relief="flat", bd=0,
                  command=self._backspace).pack(side="left", padx=1)

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=(8, 0))
        tk.Button(btn_frame, text="Cancelar", bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Guardar", bg="#0f2520", fg=CYAN,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._save).pack(side="left", padx=6)

        self.entry.bind("<Return>", lambda e: self._save())
        self.entry.bind("<Escape>", lambda e: self.destroy())

    def _type(self, ch: str):
        ch = ch.upper() if self._uppercase else ch
        pos = self.entry.index("insert")
        self.var.set(self.var.get()[:pos] + ch + self.var.get()[pos:])
        self.entry.icursor(pos + 1)

    def _backspace(self):
        pos = self.entry.index("insert")
        if pos > 0:
            val = self.var.get()
            self.var.set(val[:pos-1] + val[pos:])
            self.entry.icursor(pos - 1)

    def _toggle_case(self):
        self._uppercase = not self._uppercase

    def _save(self):
        name = self.var.get().strip()
        if name:
            self.on_save(self.mac, name)
        self.destroy()


class NetworkDashboard(tk.Tk):

    def __init__(self, config: dict):
        super().__init__()
        self.config_data   = config
        self.config_path   = config.get("_path", "config.json")
        self.subnet        = config["subnet"]
        self.scan_interval = config["scan_interval"]
        self.ping_warn     = config["ping_warn_ms"]
        self.known         = config.get("devices", {})

        self.cache = StateCache()
        self.rows: dict[str, dict] = {}
        self._scanning = False
        self._show_mac: dict[str, bool] = {}

        self.title("Net Monitor")
        self.geometry("480x280")
        self.resizable(False, True)
        self.maxsize(480, 300)
        self.configure(bg=BG)
        self.overrideredirect(False)

        self._build_ui()
        self._start_scan_loop()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=8, pady=(6, 0))

        tk.Label(hdr, text="NET MONITOR", bg=BG, fg=CYAN,
                 font=F_TITLE).pack(side="left")

        # Botón de configuración — discreto, solo un ícono de engranaje
        tk.Button(hdr, text="⚙", bg=BG, fg=MUTED,
                  font=("monospace", 11), relief="flat", bd=0,
                  activebackground=BG, activeforeground=CYAN,
                  cursor="hand2",
                  command=self._open_subnet_config).pack(side="left", padx=(6,0))

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

        # Subnet actual en el footer
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

    def _open_subnet_config(self):
        NumpadDialog(
            self,
            title="Subred  (ej: 192.168.0.0/24)",
            value=self.subnet,
            on_save=self._save_subnet
        )

    def _save_subnet(self, value: str):
        # Validación mínima
        if "/" not in value:
            value += "/24"
        self.subnet = value
        self.config_data["subnet"] = value
        self.lbl_subnet.config(text=value)
        self._persist_config()
        # Limpiar filas y re-escanear con la nueva subred
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.rows.clear()
        self._show_mac.clear()
        self._force_scan()

    def _persist_config(self):
        try:
            with open(self.config_path, "w") as f:
                data = {k: v for k, v in self.config_data.items()
                        if not k.startswith("_")}
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[gui] Error guardando config: {e}")

    def _make_row(self, mac: str):
        frame = tk.Frame(self.list_frame, bg=BG2, pady=2)
        frame.pack(fill="x", pady=1)

        dot = tk.Label(frame, text="●", bg=BG2, fg=MUTED,
                       font=F_SMALL, width=2)
        name = tk.Label(frame, text="", bg=BG2, fg=CYAN,
                        font=F_NORMAL, width=COL_NAME, anchor="w",
                        cursor="hand2")
        lbl_ip = tk.Label(frame, text="", bg=BG2, fg=BLUE,
                          font=F_SMALL, width=COL_IP, anchor="w",
                          cursor="hand2")
        vendor = tk.Label(frame, text="", bg=BG2, fg=MUTED,
                          font=F_SMALL, width=COL_VENDOR, anchor="w")
        ping = tk.Label(frame, text="---", bg=BG2, fg=MUTED,
                        font=F_NORMAL, width=COL_PING, anchor="e")

        for w in (dot, name, lbl_ip, vendor, ping):
            w.pack(side="left", padx=1)

        name.bind("<Button-1>", lambda e, m=mac: self._open_rename(m))
        lbl_ip.bind("<Button-1>", lambda e, m=mac: self._toggle_ip_mac(m))

        self._show_mac[mac] = False
        self.rows[mac] = {"frame": frame, "dot": dot, "name": name,
                          "lbl_ip": lbl_ip, "vendor": vendor,
                          "ping": ping, "ip": "", "mac": mac}

    def _toggle_ip_mac(self, mac: str):
        self._show_mac[mac] = not self._show_mac.get(mac, False)
        row = self.rows[mac]
        if self._show_mac[mac]:
            row["lbl_ip"].config(text=mac[:COL_IP], fg=MUTED)
        else:
            row["lbl_ip"].config(text=row["ip"][:COL_IP], fg=BLUE)

    def _open_rename(self, mac: str):
        info = self.known.get(mac, {})
        current = info.get("name", mac)
        ip = self.rows[mac]["ip"]
        RenameDialog(self, mac, ip, current, self._save_name)

    def _save_name(self, mac: str, name: str):
        if mac not in self.known:
            self.known[mac] = {}
        self.known[mac]["name"] = name
        self.config_data["devices"] = self.known
        self._persist_config()
        if mac in self.rows:
            self.rows[mac]["name"].config(text=name[:COL_NAME])

    def _update_row(self, device: dict):
        mac = device["mac"]
        ip  = device["ip"]
        if mac not in self.rows:
            self._make_row(mac)

        row = self.rows[mac]
        row["ip"] = ip

        info = self.known.get(mac, {})
        label = info.get("name", ip.split(".")[-1])
        vendor_str = device.get("vendor", "")[:COL_VENDOR]
        p = device.get("ping_ms")

        row["name"].config(text=label[:COL_NAME])
        row["vendor"].config(text=vendor_str)

        if not self._show_mac.get(mac, False):
            row["lbl_ip"].config(text=ip[:COL_IP], fg=BLUE)

        if p is None:
            row["dot"].config(fg=RED)
            row["ping"].config(text="---", fg=RED)
        else:
            ms = int(float(p))
            color = ORANGE if ms > self.ping_warn else GREEN
            row["dot"].config(fg=GREEN)
            row["ping"].config(text=f"{ms}ms", fg=color)

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
        self.lbl_counts.config(text=f"▲{online}  ▼{offline}  total {len(devices)}")
        self.lbl_last.config(text=f"scan {datetime.now().strftime('%H:%M:%S')}")
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

    def _tick_clock(self):
        self.lbl_time.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick_clock)
