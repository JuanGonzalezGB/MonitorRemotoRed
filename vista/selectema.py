"""
view/selectema.py — selector de temas con estética tipo dashboard
"""
import tkinter as tk
from vista.gui_dictionary import FORMATS
from vista.gui_dictionary import TEMAS
from controlador.controladorTemas import ControladorTemas
import sys
import os
import subprocess

F_TITLE  = FORMATS["F_TITLE"]
F_NORMAL = FORMATS["F_NORMAL"]
F_SMALL  = FORMATS["F_SMALL"]


class ThemeSelector(tk.Toplevel):
    def __init__(self, parent, estilo):
        super().__init__(parent)
        self.estilo = estilo
        self.controladorTema = ControladorTemas(self)

        self.title("Themes")
        self.geometry("480x260")
        self.resizable(False, False)
        self.configure(bg=self.estilo.bg)

        self.tipo = tk.StringVar(value=self._traduz())

        self._build_ui()

    # ── UI ─────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=self.estilo.bg)
        hdr.pack(fill="x", padx=8, pady=(6, 0))

        tk.Label(
            hdr,
            text="THEMES",
            bg=self.estilo.bg,
            fg=self.estilo.cyan,
            font=F_TITLE
        ).pack(side="left")

        tk.Button(
            hdr,
            text="✕",
            bg=self.estilo.bg,
            fg=self.estilo.muted,
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=self.estilo.bg,
            activeforeground=self.estilo.cyan,
            command=self.destroy
        ).pack(side="right")

        # Divider
        tk.Frame(self, bg=self.estilo.border, height=1).pack(fill="x", padx=8, pady=4)

        # Body
        body = tk.Frame(self, bg=self.estilo.bg)
        body.pack(fill="both", expand=True, padx=12, pady=10)

        tk.Label(
            body,
            text="Seleccionar tema",
            bg=self.estilo.bg,
            fg=self.estilo.muted,
            font=F_NORMAL,
            anchor="w"
        ).pack(fill="x", pady=(0, 6))

        self.menu = tk.OptionMenu(body, self.tipo, *TEMAS.keys(), command=self._preview)
        self.menu.config(
            bg=self.estilo.bg2,
            fg=self.estilo.cyan,
            activebackground=self.estilo.bg2,
            activeforeground=self.estilo.cyan,
            highlightthickness=1,
            highlightbackground=self.estilo.border,
            bd=0
        )
        self.menu.pack(fill="x", pady=(0, 10))

        # Preview label (opcional visual)
        self.lbl_preview = tk.Label(
            body,
            text="Vista previa",
            bg=self.estilo.bg2,
            fg=self.estilo.muted,
            font=F_SMALL,
            height=4
        )
        self.lbl_preview.pack(fill="x", pady=6)

        # Divider
        tk.Frame(self, bg=self.estilo.border, height=1).pack(fill="x", padx=8, pady=4)

        # Footer
        ftr = tk.Frame(self, bg=self.estilo.bg)
        ftr.pack(fill="x", padx=8, pady=(0, 6))

        tk.Button(
            ftr,
            text="Cancelar",
            bg=self.estilo.bg,
            fg=self.estilo.muted,
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=self.estilo.bg,
            activeforeground=self.estilo.cyan,
            command=self.destroy
        ).pack(side="left")

        tk.Button(
            ftr,
            text="Aplicar",
            bg=self.estilo.boton,
            fg=self.estilo.cyan,
            relief="flat",
            bd=0,
            padx=10,
            cursor="hand2",
            command=self._apply
        ).pack(side="right")

    # ── Lógica ─────────────────────────────────────────

    def _traduz(self):
        codigoANombre = {v: k for k, v in TEMAS.items()}
        return codigoANombre.get(self.estilo.getNombre(), "Oscuro")
    
    def _preview(self, _=None):
        tema = TEMAS.get(self.tipo.get(), "dark")
        self.controladorTema.aplicarTema(tema)

    def _apply(self):
        tema = TEMAS.get(self.tipo.get(), "dark")
        self.controladorTema.aceptarTema(tema)

        self.destroy()
        self.master.destroy()

        subprocess.Popen([sys.executable, "main.py"])

     