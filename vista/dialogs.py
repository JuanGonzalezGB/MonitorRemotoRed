"""
view/dialogs.py — diálogos: renombrar dispositivo y configurar subred
"""
import tkinter as tk
from typing import Callable

from vista.keyboards import VirtualKeyboard, Numpad
from vista.gui_dictionary import FORMATS

F_NORMAL = FORMATS["F_NORMAL"]
F_SMALL  = FORMATS["F_SMALL"]


class RenameDialog(tk.Toplevel):
    def __init__(self, parent, mac: str, ip: str,
                 current_name: str,
                 on_save: Callable[[str, str], None],
                 on_delete: Callable[[str], None],
                 estilo):
        super().__init__(parent)
        self.estilo    = estilo
        self.on_save   = on_save
        self.on_delete = on_delete
        self.mac       = mac
        self.ip        = ip
        self.overrideredirect(True)
        self.configure(bg=self.estilo.bg)
        self.geometry(f"480x250+{parent.winfo_x()}+{parent.winfo_y()}")
        self._build(current_name)
        self.after(10, self.grab_set)

    def _build(self, current_name: str):
        # ── Footer fijo abajo ──────────────────────────────────────────────
        bf = tk.Frame(self, bg=self.estilo.bg)
        bf.pack(side="bottom", pady=(4, 10))

        tk.Button(bf, text="🗑", bg=self.estilo.bg, fg=self.estilo.red,
                  font=("monospace", 12), relief="flat", bd=0, padx=8,
                  activebackground=self.estilo.bg, activeforeground=self.estilo.red,
                  cursor="hand2",
                  command=self._confirm_delete).pack(side="left", padx=(0, 20))

        tk.Button(bf, text="Cancelar", bg=self.estilo.bg2, fg=self.estilo.muted,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Guardar", bg="#0f2520", fg=self.estilo.cyan,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._save).pack(side="left", padx=6)

        # ── Contenido ──────────────────────────────────────────────────────
        tk.Label(self, text=f"Renombrar  {self.ip}  ({self.mac})",
                 bg=self.estilo.bg, fg=self.estilo.cyan, font=F_SMALL).pack(pady=(12, 4))

        ef = tk.Frame(self, bg=self.estilo.border, padx=1, pady=1)
        ef.pack(padx=24, fill="x")
        self.entry = tk.Entry(ef, bg=self.estilo.bg2, fg=self.estilo.white,
                              insertbackground=self.estilo.cyan,
                              font=("monospace", 12), relief="flat", bd=4)
        self.entry.insert(0, current_name)
        self.entry.pack(fill="x")
        self.entry.focus_set()
        self.entry.icursor("end")

        VirtualKeyboard(self.estilo, self, self.entry).pack(pady=(8, 0), padx=8)

        self.entry.bind("<Return>", lambda e: self._save())
        self.entry.bind("<Escape>", lambda e: self.destroy())

    def _confirm_delete(self):
        ConfirmDialog(
            self,
            message=f"¿Eliminar nombre guardado\nde {self.ip}\n({self.mac})?",
            on_confirm=self._delete,
            estilo=self.estilo,
        )

    def _delete(self):
        self.on_delete(self.mac)
        self.destroy()

    def _save(self):
        name = self.entry.get().strip()
        if name:
            self.on_save(self.mac, name)
        self.destroy()


class ConfirmDialog(tk.Toplevel):
    def __init__(self, parent, message: str,
                 on_confirm: Callable, estilo):
        super().__init__(parent)
        self.estilo     = estilo
        self.on_confirm = on_confirm
        self.overrideredirect(True)
        self.configure(bg=self.estilo.bg)
        self.geometry(f"300x140+{parent.winfo_x() + 90}+{parent.winfo_y() + 55}")
        self._build(message)
        self.after(10, self.grab_set)

    def _build(self, message: str):
        tk.Frame(self, bg=self.estilo.border, height=1).pack(fill="x")
        tk.Label(self, text=message, bg=self.estilo.bg, fg=self.estilo.white,
                 font=F_SMALL, justify="center").pack(expand=True, pady=(20, 12))
        tk.Frame(self, bg=self.estilo.border, height=1).pack(fill="x")

        bf = tk.Frame(self, bg=self.estilo.bg)
        bf.pack(pady=(8, 10))
        tk.Button(bf, text="Cancelar", bg=self.estilo.bg2, fg=self.estilo.muted,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Eliminar", bg=self.estilo.bg2, fg=self.estilo.red,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._confirm).pack(side="left", padx=6)

    def _confirm(self):
        self.on_confirm()
        self.destroy()


class NumpadDialog(tk.Toplevel):
    def __init__(self, parent, title: str, value: str,
                 on_save: Callable[[str], None], estilo):  # ← estilo agregado
        super().__init__(parent)
        self.estilo = estilo                               # ← asignado antes de _build
        self.on_save = on_save
        self.overrideredirect(True)
        self.configure(bg=self.estilo.bg)
        self.geometry(f"480x250+{parent.winfo_x()}+{parent.winfo_y()}")
        self._build(title, value)
        self.grab_set()

    def _build(self, title: str, value: str):
        # ── Footer fijo abajo ──────────────────────────────────────────────
        bf = tk.Frame(self, bg=self.estilo.bg)
        bf.pack(side="bottom", pady=(4, 10))
        tk.Button(bf, text="Cancelar", bg=self.estilo.bg2, fg=self.estilo.muted,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Guardar", bg="#0f2520", fg=self.estilo.cyan,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._save).pack(side="left", padx=6)

        # ── Contenido ──────────────────────────────────────────────────────
        tk.Label(self, text=title, bg=self.estilo.bg, fg=self.estilo.cyan,
                 font=F_SMALL).pack(pady=(8, 4))

        ef = tk.Frame(self, bg=self.estilo.border, padx=1, pady=1)
        ef.pack(padx=60, fill="x")
        self.entry = tk.Entry(ef, bg=self.estilo.bg2, fg=self.estilo.white,
                              insertbackground=self.estilo.cyan,
                              font=("monospace", 11), relief="flat", bd=3,
                              justify="center")
        self.entry.insert(0, value)
        self.entry.pack(fill="x")
        self.entry.focus_set()
        self.entry.icursor("end")

        Numpad(self.estilo, self, self.entry).pack(pady=(8, 0))  # ← estilo agregado

        self.entry.bind("<Return>", lambda e: self._save())
        self.entry.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        val = self.entry.get().strip()
        if val:
            self.on_save(val)
        self.destroy()