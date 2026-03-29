"""
view/dialogs.py — diálogos: renombrar dispositivo y configurar subred
"""
import tkinter as tk
from typing import Callable

from vista.keyboards import VirtualKeyboard, Numpad
from vista.gui_dictionary import COLORS, FORMATS

BG      = COLORS["BG"]
BG2     = COLORS["BG2"]
BORDER  = COLORS["BORDER"]
COLOR1    = COLORS["CYAN"]
COLOR2   = COLORS["WHITE"]
MUTED   = COLORS["MUTED"]



F_NORMAL = FORMATS["F_NORMAL"]
F_SMALL  = FORMATS["F_SMALL"]


class RenameDialog(tk.Toplevel):
    def __init__(self, parent, mac: str, ip: str,
                 current_name: str, on_save: Callable[[str, str], None]):
        super().__init__(parent)
        self.on_save = on_save
        self.mac = mac
        self.ip = ip
        self.overrideredirect(True)
        self.configure(bg=BG)
        self.geometry(f"480x300+{parent.winfo_x()}+{parent.winfo_y()}")
        self._build(current_name)
        self.grab_set()

    def _build(self, current_name: str):
        tk.Label(self, text=f"Renombrar  {self.ip}  ({self.mac})",
                 bg=BG, fg=COLOR1, font=F_SMALL).pack(pady=(12, 4))

        ef = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        ef.pack(padx=24, fill="x")
        self.entry = tk.Entry(ef, bg=BG2, fg=COLOR2, insertbackground=COLOR1,
                              font=("monospace", 12), relief="flat", bd=4)
        self.entry.insert(0, current_name)
        self.entry.pack(fill="x")
        self.entry.focus_set()
        self.entry.icursor("end")

        VirtualKeyboard(self, self.entry).pack(pady=(8, 0), padx=8)

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(8, 0))
        tk.Button(bf, text="Cancelar", bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Guardar", bg="#0f2520", fg=COLOR1,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._save).pack(side="left", padx=6)

        self.entry.bind("<Return>", lambda e: self._save())
        self.entry.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        name = self.entry.get().strip()
        if name:
            self.on_save(self.mac, name)
        self.destroy()


class NumpadDialog(tk.Toplevel):
    def __init__(self, parent, title: str, value: str,
                 on_save: Callable[[str], None]):
        super().__init__(parent)
        self.on_save = on_save
        self.overrideredirect(True)
        self.configure(bg=BG)
        self.geometry(f"480x300+{parent.winfo_x()}+{parent.winfo_y()}")
        self._build(title, value)
        self.grab_set()

    def _build(self, title: str, value: str):
        tk.Label(self, text=title, bg=BG, fg=COLOR1,
                 font=F_SMALL).pack(pady=(8, 4))

        ef = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        ef.pack(padx=60, fill="x")
        self.entry = tk.Entry(ef, bg=BG2, fg=COLOR2, insertbackground=COLOR1,
                              font=("monospace", 11), relief="flat", bd=3,
                              justify="center")
        self.entry.insert(0, value)
        self.entry.pack(fill="x")
        self.entry.focus_set()
        self.entry.icursor("end")

        Numpad(self, self.entry).pack(pady=(8, 0))

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(10, 0))
        tk.Button(bf, text="Cancelar", bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Guardar", bg="#0f2520", fg=COLOR1,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._save).pack(side="left", padx=6)

        self.entry.bind("<Return>", lambda e: self._save())
        self.entry.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        val = self.entry.get().strip()
        if val:
            self.on_save(val)
        self.destroy()
