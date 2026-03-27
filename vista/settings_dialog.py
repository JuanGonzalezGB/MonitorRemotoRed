"""
view/settings_dialog.py — diálogo de configuración: subred y tiempo de refresco
"""
import tkinter as tk
from typing import Callable

from vista.keyboards import Numpad

BG      = "#0f0f12"
BG2     = "#161620"
BORDER  = "#1e1e2a"
CYAN    = "#7fd4c1"
WHITE   = "#e0e0e8"
MUTED   = "#4a4a5a"
ORANGE  = "#f0a030"

F_NORMAL = ("monospace", 9)
F_SMALL  = ("monospace", 8)


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent,
                 current_subnet: str,
                 current_interval: int,
                 on_save: Callable[[str, int], None]):
        super().__init__(parent)
        self.on_save = on_save
        self.overrideredirect(True)
        self.configure(bg=BG)
        self.geometry(f"480x300+{parent.winfo_x()}+{parent.winfo_y()}")
        self._build(current_subnet, current_interval)
        self.grab_set()

    def _build(self, subnet: str, interval: int):
        # Título
        tk.Label(self, text="Configuración", bg=BG, fg=CYAN,
                 font=F_NORMAL).pack(pady=(10, 6))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=12)

        # Campos en dos columnas
        fields = tk.Frame(self, bg=BG)
        fields.pack(fill="x", padx=20, pady=(8, 0))

        # Subred
        tk.Label(fields, text="Subred", bg=BG, fg=MUTED,
                 font=F_SMALL, width=16, anchor="w").grid(row=0, column=0, sticky="w")
        ef1 = tk.Frame(fields, bg=BORDER, padx=1, pady=1)
        ef1.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self.entry_subnet = tk.Entry(ef1, bg=BG2, fg=WHITE, insertbackground=CYAN,
                                     font=("monospace", 10), relief="flat", bd=3,
                                     justify="center", width=18)
        self.entry_subnet.insert(0, subnet)
        self.entry_subnet.pack(fill="x")

        # Refresco
        tk.Label(fields, text="Refresco (seg)", bg=BG, fg=MUTED,
                 font=F_SMALL, width=16, anchor="w").grid(row=1, column=0, sticky="w", pady=(8,0))
        ef2 = tk.Frame(fields, bg=BORDER, padx=1, pady=1)
        ef2.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(8, 0))
        self.entry_interval = tk.Entry(ef2, bg=BG2, fg=WHITE, insertbackground=CYAN,
                                       font=("monospace", 10), relief="flat", bd=3,
                                       justify="center", width=18)
        self.entry_interval.insert(0, str(interval))
        self.entry_interval.pack(fill="x")

        fields.columnconfigure(1, weight=1)

        # Foco activo — click en campo activa numpad para ese campo
        self._active_entry = self.entry_subnet
        self.entry_subnet.bind("<FocusIn>", lambda e: self._set_active(self.entry_subnet))
        self.entry_interval.bind("<FocusIn>", lambda e: self._set_active(self.entry_interval))

        # Numpad compartido
        self._numpad_frame = tk.Frame(self, bg=BG)
        self._numpad_frame.pack(pady=(8, 0))
        self._numpad = Numpad(self._numpad_frame, self.entry_subnet)
        self._numpad.pack()

        # Botones
        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(8, 0))
        tk.Button(bf, text="Cancelar", bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Guardar", bg="#0f2520", fg=CYAN,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._save).pack(side="left", padx=6)

        self.entry_subnet.focus_set()

    def _set_active(self, entry: tk.Entry):
        """Redirige el numpad al campo con foco."""
        self._active_entry = entry
        self._numpad._entry = entry

    def _save(self):
        subnet = self.entry_subnet.get().strip()
        if "/" not in subnet:
            subnet += "/24"
        try:
            interval = max(1, int(self.entry_interval.get().strip()))
        except ValueError:
            interval = 2
        self.on_save(subnet, interval)
        self.destroy()
