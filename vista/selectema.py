"""
vista/selectema.py — selector de temas con estética tipo dashboard
"""
import tkinter as tk
from vista.gui_dictionary import FORMATS, TEMAS
from controlador.controladorTemas import ControladorTemas, etiquetar, ROL_BG, ROL_BG2, ROL_CYAN, ROL_MUTED, ROL_BOTON

import sys
import subprocess

F_TITLE  = FORMATS["F_TITLE"]
F_NORMAL = FORMATS["F_NORMAL"]
F_SMALL  = FORMATS["F_SMALL"]


class ThemeSelector(tk.Toplevel):
    def __init__(self, parent, estilo):
        super().__init__(parent)
        self.estilo = estilo
        self.controladorTema = ControladorTemas(self)

        # Guardar el tema original para poder revertir si se cancela
        self._tema_original = estilo.getNombre()

        self.title("Themes")
        self.geometry("480x255")
        self.resizable(False, False)
        self.configure(bg=self.estilo.bg)

        self.tipo = tk.StringVar(value=self._traduz())
        self._build_ui()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=self.estilo.bg)
        etiquetar(hdr, ROL_BG)
        hdr.pack(fill="x", padx=8, pady=(6, 0))

        lbl = tk.Label(hdr, text="THEMES", bg=self.estilo.bg,
                       fg=self.estilo.cyan, font=F_TITLE)
        etiquetar(lbl, ROL_BG, ROL_CYAN)
        lbl.pack(side="left")

        btn_x = tk.Button(hdr, text="✕", bg=self.estilo.bg, fg=self.estilo.muted,
                          relief="flat", bd=0, cursor="hand2",
                          activebackground=self.estilo.bg, activeforeground=self.estilo.cyan,
                          command=self._cancel)
        etiquetar(btn_x, ROL_BG, ROL_MUTED)
        btn_x.pack(side="right")

        sep1 = tk.Frame(self, bg=self.estilo.border, height=1)
        sep1._bg_rol = "border"
        sep1.pack(fill="x", padx=8, pady=4)

        body = tk.Frame(self, bg=self.estilo.bg)
        etiquetar(body, ROL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=10)

        lbl_sel = tk.Label(body, text="Seleccionar tema", bg=self.estilo.bg,
                           fg=self.estilo.muted, font=F_NORMAL, anchor="w")
        etiquetar(lbl_sel, ROL_BG, ROL_MUTED)
        lbl_sel.pack(fill="x", pady=(0, 6))

        self.menu = tk.OptionMenu(body, self.tipo, *TEMAS.keys(), command=self._preview)
        self.menu.config(
            bg=self.estilo.bg2, fg=self.estilo.cyan,
            activebackground=self.estilo.bg2, activeforeground=self.estilo.cyan,
            highlightthickness=1, highlightbackground=self.estilo.border, bd=0
        )
        etiquetar(self.menu, ROL_BG2, ROL_CYAN)
        self.menu.pack(fill="x", pady=(0, 10))

        self.lbl_preview = tk.Label(body, text="Vista previa",
                                    bg=self.estilo.bg2, fg=self.estilo.muted,
                                    font=F_SMALL, height=4)
        etiquetar(self.lbl_preview, ROL_BG2, ROL_MUTED)
        self.lbl_preview.pack(fill="x", pady=6)

        sep2 = tk.Frame(self, bg=self.estilo.border, height=1)
        sep2._bg_rol = "border"
        sep2.pack(fill="x", padx=8, pady=4)

        ftr = tk.Frame(self, bg=self.estilo.bg)
        etiquetar(ftr, ROL_BG)
        ftr.pack(fill="x", padx=8, pady=(0, 6))

        btn_cancel = tk.Button(ftr, text="Cancelar", bg=self.estilo.bg, fg=self.estilo.muted,
                               relief="flat", bd=0, cursor="hand2",
                               activebackground=self.estilo.bg, activeforeground=self.estilo.cyan,
                               command=self._cancel)
        etiquetar(btn_cancel, ROL_BG, ROL_MUTED)
        btn_cancel.pack(side="left")

        btn_apply = tk.Button(ftr, text="Aplicar", bg=self.estilo.boton, fg=self.estilo.cyan,
                              relief="flat", bd=0, padx=10, cursor="hand2",
                              command=self._apply)
        etiquetar(btn_apply, ROL_BOTON, ROL_CYAN)
        btn_apply.pack(side="right")

    def _traduz(self):
        codigoANombre = {v: k for k, v in TEMAS.items()}
        return codigoANombre.get(self.estilo.getNombre(), "Oscuro")

    def _preview(self, _=None):
        tema = TEMAS.get(self.tipo.get(), "dark")
        self.controladorTema.aplicarTema(tema)

    def _cancel(self):
        # Revertir al tema original antes de cerrar
        self.controladorTema.aplicarTema(self._tema_original)
        self.destroy()

    def _apply(self):
        tema = TEMAS.get(self.tipo.get(), "dark")
        self.controladorTema.aceptarTema(tema)
        self.destroy()
