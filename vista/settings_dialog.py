"""
view/settings_dialog.py — configuración: subred, refresco y MongoDB
Todo dentro del scroll, teclado incluido.
"""
import tkinter as tk
from typing import Callable

from vista.keyboards import Numpad, VirtualKeyboard

BG      = "#0f0f12"
BG2     = "#161620"
BORDER  = "#1e1e2a"
CYAN    = "#7fd4c1"
WHITE   = "#e0e0e8"
MUTED   = "#4a4a5a"

F_NORMAL = ("monospace", 9)
F_SMALL  = ("monospace", 8)


def _labeled_entry(parent, label: str, value: str, show: str = "") -> tk.Entry:
    row = tk.Frame(parent, bg=BG)
    row.pack(fill="x", pady=(4, 0))
    tk.Label(row, text=label, bg=BG, fg=MUTED,
             font=F_SMALL, width=16, anchor="w").pack(side="left")
    ef = tk.Frame(row, bg=BORDER, padx=1, pady=1)
    ef.pack(side="left", fill="x", expand=True)
    entry = tk.Entry(ef, bg=BG2, fg=WHITE, insertbackground=CYAN,
                     font=("monospace", 9), relief="flat", bd=2, show=show)
    entry.insert(0, value)
    entry.pack(fill="x")
    return entry


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent,
                 current_subnet: str,
                 current_interval: int,
                 current_mongo: dict,
                 on_save: Callable[[str, int, dict], None]):
        super().__init__(parent)
        self.on_save = on_save
        self.overrideredirect(True)
        self.configure(bg=BG)
        self.geometry(f"480x300+{parent.winfo_x()}+{parent.winfo_y()}")
        self._kb_frame: tk.Frame | None = None
        self._build(current_subnet, current_interval, current_mongo)
        self.grab_set()

    def _build(self, subnet: str, interval: int, mongo: dict):
        # Título fijo arriba
        tk.Label(self, text="Configuración", bg=BG, fg=CYAN,
                 font=F_NORMAL).pack(pady=(8, 4))
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=12)

        # Botones fijos abajo
        bf = tk.Frame(self, bg=BG)
        bf.pack(side="bottom", pady=(4, 6))
        tk.Button(bf, text="Cancelar", bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Guardar", bg="#0f2520", fg=CYAN,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self._save).pack(side="left", padx=6)

        tk.Frame(self, bg=BORDER, height=1).pack(side="bottom", fill="x", padx=12)

        # Canvas + scrollbar — ocupa el espacio restante
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=12, pady=(4, 0))

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._scroll_frame = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(e):
            canvas.itemconfig(win, width=e.width)

        self._scroll_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_wheel)

        # ── Campos de red ─────────────────────────────────────────────────────
        tk.Label(self._scroll_frame, text="Red", bg=BG, fg=CYAN,
                 font=F_SMALL).pack(anchor="w", pady=(4, 2))

        self.e_subnet   = _labeled_entry(self._scroll_frame, "Subred", subnet)
        self.e_interval = _labeled_entry(self._scroll_frame, "Refresco (seg)", str(interval))

        tk.Frame(self._scroll_frame, bg=BORDER, height=1).pack(fill="x", pady=(8, 2))

        # ── Campos MongoDB ────────────────────────────────────────────────────
        tk.Label(self._scroll_frame, text="MongoDB", bg=BG, fg=CYAN,
                 font=F_SMALL).pack(anchor="w", pady=(0, 2))

        self.e_host = _labeled_entry(self._scroll_frame, "Host", mongo.get("host", ""))
        self.e_port = _labeled_entry(self._scroll_frame, "Puerto", str(mongo.get("port", 27017)))
        self.e_user = _labeled_entry(self._scroll_frame, "Usuario", mongo.get("user", ""))
        self.e_pass = _labeled_entry(self._scroll_frame, "Contraseña",
                                     mongo.get("password", ""), show="●")
        self.e_db   = _labeled_entry(self._scroll_frame, "Base de datos",
                                     mongo.get("db", "scanner"))

        tk.Frame(self._scroll_frame, bg=BORDER, height=1).pack(fill="x", pady=(8, 2))

        # ── Teclado dentro del scroll ─────────────────────────────────────────
        self._kb_frame = tk.Frame(self._scroll_frame, bg=BG)
        self._kb_frame.pack(pady=(4, 8))

        # Binds de foco
        numpad_fields = {self.e_subnet, self.e_interval, self.e_host, self.e_port}
        qwerty_fields = {self.e_user, self.e_pass, self.e_db}

        for entry in numpad_fields:
            entry.bind("<FocusIn>", lambda e, en=entry: self._show_kb(en, "numpad"))
        for entry in qwerty_fields:
            entry.bind("<FocusIn>", lambda e, en=entry: self._show_kb(en, "qwerty"))

        # Mostrar numpad por defecto
        self.e_subnet.focus_set()
        self._show_kb(self.e_subnet, "numpad")

    def _show_kb(self, entry: tk.Entry, kb_type: str):
        for w in self._kb_frame.winfo_children():
            w.destroy()
        if kb_type == "numpad":
            Numpad(self._kb_frame, entry).pack()
        else:
            VirtualKeyboard(self._kb_frame, entry).pack()

    def _save(self):
        subnet = self.e_subnet.get().strip()
        if "/" not in subnet:
            subnet += "/24"
        try:
            interval = max(1, int(self.e_interval.get().strip()))
        except ValueError:
            interval = 2

        mongo = {
            "host":     self.e_host.get().strip(),
            "port":     int(self.e_port.get().strip() or 27017),
            "user":     self.e_user.get().strip(),
            "password": self.e_pass.get(),
            "db":       self.e_db.get().strip() or "scanner",
        }

        self.on_save(subnet, interval, mongo)
        self.destroy()
