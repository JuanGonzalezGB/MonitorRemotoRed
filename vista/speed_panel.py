# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Juan S.G. Castellanos
"""
view/speed_panel.py — panel flotante de velocidad del host
"""
import tkinter as tk
from modelo.bandwidth import BandwidthMonitor
from vista.gui_dictionary import FORMATS, GRAPHFORMAT
import subprocess
F_NORMAL = FORMATS["F_NORMAL"]
F_SMALL  = FORMATS["F_SMALL"]

GRAPH_W = GRAPHFORMAT["GRAPH_W"]
GRAPH_H = GRAPHFORMAT["GRAPH_H"]


def fmt_mbps(kbs: float) -> str:
    mbps = kbs * 8 / 1024
    return f"{mbps:.1f} Mbps"


def fmt_kbs(kbs: float) -> str:
    if kbs >= 1024:
        return f"{kbs/1024:.1f} MB/s"
    return f"{kbs:.1f} KB/s"


class SpeedPanel(tk.Toplevel):
    def __init__(self, estilo, parent, label: str, ip: str,
                mac: str, bw: BandwidthMonitor):
        super().__init__(parent)
        self.estilo = estilo
        self.bw = bw
        self.ip = ip
        self._running = True
        # ── ya no inicializa peak en 0 — lo toma del monitor ──
        # self._peak_rx = 0.0   ← eliminar
        # self._peak_tx = 0.0   ← eliminar

        self.overrideredirect(True)
        self.configure(bg=self.estilo.bg)
        self.geometry(f"480x200+{parent.winfo_x()}+{parent.winfo_y()}")
        self._build(label, mac)
        self.grab_set()
        self._update()

    def _build(self, label: str, mac: str):
        hdr = tk.Frame(self, bg=self.estilo.bg)
        hdr.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(hdr, text=f"{label}  {self.ip}", bg=self.estilo.bg, fg=self.estilo.cyan,
                 font=F_NORMAL).pack(side="left")
        tk.Label(hdr, text=mac, bg=self.estilo.bg, fg=self.estilo.muted,
                 font=F_SMALL).pack(side="left", padx=8)
        tk.Button(hdr, text="✕", bg=self.estilo.bg, fg=self.estilo.muted, font=F_SMALL,
                  relief="flat", bd=0, command=self._close).pack(side="right")

        tk.Frame(self, bg=self.estilo.border, height=1).pack(fill="x", padx=8)

        stats = tk.Frame(self, bg=self.estilo.bg)
        stats.pack(fill="x", padx=10, pady=(6, 2))
        self.lbl_rx = tk.Label(stats, text="↓  0.0 KB/s", bg=self.estilo.bg,
                               fg=self.estilo.cyan, font=("monospace", 10))
        self.lbl_rx.pack(side="left", padx=(0, 20))
        self.lbl_tx = tk.Label(stats, text="↑  0.0 KB/s", bg=self.estilo.bg,
                               fg=self.estilo.red, font=("monospace", 10))
        self.lbl_tx.pack(side="left")
        tk.Label(stats, text="(este equipo)", bg=self.estilo.bg, fg=self.estilo.muted,
                 font=F_SMALL).pack(side="right")

        self.canvas = tk.Canvas(self, width=GRAPH_W, height=GRAPH_H,
                                bg=self.estilo.bg2, highlightthickness=0)
        self.canvas.pack(padx=10, pady=(4, 0))

        leg = tk.Frame(self, bg=self.estilo.bg)
        leg.pack(fill="x", padx=10, pady=(4, 6))
        rx_col = tk.Frame(leg, bg=self.estilo.bg)
        rx_col.pack(side="left")
        self.lbl_rx_mbps = tk.Label(rx_col, text="— descarga  0.0 Mbps",
                                     bg=self.estilo.bg, fg=self.estilo.cyan, font=F_SMALL)
        self.lbl_rx_mbps.pack(anchor="w")
        self.lbl_rx_peak = tk.Label(rx_col, text="  peak  0.0 Mbps",
                                     bg=self.estilo.bg, fg=self.estilo.muted, font=F_SMALL)
        self.lbl_rx_peak.pack(anchor="w")

        tx_col = tk.Frame(leg, bg=self.estilo.bg)
        tx_col.pack(side="left", padx=12)
        self.lbl_tx_mbps = tk.Label(tx_col, text="— subida  0.0 Mbps",
                                     bg=self.estilo.bg, fg=self.estilo.red, font=F_SMALL)
        self.lbl_tx_mbps.pack(anchor="w")
        self.lbl_tx_peak = tk.Label(tx_col, text="  peak  0.0 Mbps",
                                     bg=self.estilo.bg, fg=self.estilo.muted, font=F_SMALL)
        self.lbl_tx_peak.pack(anchor="w")
        tk.Button(leg, text="Cerrar", bg=self.estilo.bg2, fg=self.estilo.muted,
                  font=F_SMALL, relief="flat", bd=0, padx=8,
                  command=self._close).pack(side="right")
        tk.Button(leg, text="Clean", bg=self.estilo.bg2, fg=self.estilo.muted,
          font=F_SMALL, relief="flat", bd=0, padx=8,
          command=self.bw.reset_peak).pack(side="right", padx=(0, 8))
        
            
        tk.Button(leg, text="SpeedTest", bg=self.estilo.bg2, fg=self.estilo.muted,
        font=F_SMALL, relief="flat", bd=0, padx=8,
        command=lambda: self._speedtest()).pack(side="left", padx=(0, 8))  
    
    def _speedtest(self):
        try:
            print("intentando speedtest")
            subprocess.Popen(["speedtest"])
        except:
            print("uff bro instala speedtest de ookla")  

    def _update(self):
        if not self._running:
            return
        rx, tx = self.bw.current()
        rx_hist, tx_hist = self.bw.history()
        peak_rx, peak_tx = self.bw.peak()          # ← lee del monitor

        self.lbl_rx.config(text=f"↓  {fmt_kbs(rx)}")
        self.lbl_tx.config(text=f"↑  {fmt_kbs(tx)}")
        self.lbl_rx_mbps.config(text=f"— descarga  {fmt_mbps(rx)}")
        self.lbl_tx_mbps.config(text=f"— subida  {fmt_mbps(tx)}")
        self.lbl_rx_peak.config(text=f"  peak  {fmt_mbps(peak_rx)}")  # ← usa peak del monitor
        self.lbl_tx_peak.config(text=f"  peak  {fmt_mbps(peak_tx)}")  # ← usa peak del monitor
        self._draw_graph(rx_hist, tx_hist)
        self.after(1000, self._update)

    def _draw_graph(self, rx_hist: list, tx_hist: list):
        self.canvas.delete("all")
        if not rx_hist and not tx_hist:
            self.canvas.create_text(GRAPH_W // 2, GRAPH_H // 2,
                                    text="recopilando datos...",
                                    fill=self.estilo.muted, font=F_SMALL)
            return

        max_val = max(max(rx_hist + tx_hist), 0.1)

        def draw_line(hist, color):
            if len(hist) < 2:
                return
            n = len(hist)
            pts = []
            for i, v in enumerate(hist):
                x = int(i / (n - 1) * (GRAPH_W - 4)) + 2
                y = int(GRAPH_H - 4 - (v / max_val) * (GRAPH_H - 8))
                pts.extend([x, y])
            self.canvas.create_line(pts, fill=color, width=1, smooth=True)

        for pct in [0.25, 0.5, 0.75]:
            y = int(GRAPH_H - 4 - pct * (GRAPH_H - 8))
            self.canvas.create_line(2, y, GRAPH_W - 2, y,
                                    fill=self.estilo.border, width=1)

        draw_line(rx_hist, self.estilo.cyan)
        draw_line(tx_hist, self.estilo.red)
        self.canvas.create_text(GRAPH_W - 4, 4, text=fmt_kbs(max_val),
                                fill=self.estilo.muted, font=F_SMALL, anchor="ne")

    def _close(self):
        self._running = False
        self.destroy()
