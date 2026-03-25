"""
view/dialogs.py — diálogos: renombrar dispositivo y configurar subred
"""
import tkinter as tk
from typing import Callable

BG      = "#0f0f12"
BG2     = "#161620"
BORDER  = "#1e1e2a"
ORANGE  = "#f0a030"
CYAN    = "#7fd4c1"
WHITE   = "#e0e0e8"
MUTED   = "#4a4a5a"

F_NORMAL = ("monospace", 9)
F_SMALL  = ("monospace", 8)


class RenameDialog(tk.Toplevel):
    KEYS = [
        list("1234567890"),
        list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm-_"),
    ]

    def __init__(self, parent, mac: str, ip: str,
                 current_name: str, on_save: Callable[[str, str], None]):
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

        ef = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        ef.pack(padx=24, fill="x")
        self.var = tk.StringVar(value=current_name)
        self.entry = tk.Entry(ef, textvariable=self.var, bg=BG2, fg=WHITE,
                              insertbackground=CYAN, font=("monospace", 12),
                              relief="flat", bd=4)
        self.entry.pack(fill="x")
        self.entry.focus_set()
        self.entry.icursor("end")

        kb = tk.Frame(self, bg=BG)
        kb.pack(pady=(8, 0), padx=8)
        for row in self.KEYS:
            rf = tk.Frame(kb, bg=BG)
            rf.pack()
            for ch in row:
                tk.Button(rf, text=ch, width=3, bg=BG2, fg=WHITE,
                          font=F_SMALL, relief="flat", bd=0,
                          activebackground=BORDER, activeforeground=CYAN,
                          command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        sp = tk.Frame(kb, bg=BG)
        sp.pack(pady=(2, 0))
        tk.Button(sp, text="ABC", width=4, bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0,
                  command=self._toggle_case).pack(side="left", padx=1)
        tk.Button(sp, text="espacio", width=8, bg=BG2, fg=WHITE,
                  font=F_SMALL, relief="flat", bd=0,
                  command=lambda: self._type(" ")).pack(side="left", padx=1)
        tk.Button(sp, text="⌫", width=4, bg=BG2, fg=ORANGE,
                  font=F_SMALL, relief="flat", bd=0,
                  command=self._backspace).pack(side="left", padx=1)

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(8, 0))
        tk.Button(bf, text="Cancelar", bg=BG2, fg=MUTED,
                  font=F_SMALL, relief="flat", bd=0, padx=12,
                  command=self.destroy).pack(side="left", padx=6)
        tk.Button(bf, text="Guardar", bg="#0f2520", fg=CYAN,
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
        tk.Label(self, text=title, bg=BG, fg=CYAN,
                 font=F_SMALL).pack(pady=(8, 4))

        ef = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        ef.pack(padx=60, fill="x")
        self.var = tk.StringVar(value=value)
        self.entry = tk.Entry(ef, textvariable=self.var, bg=BG2, fg=WHITE,
                              insertbackground=CYAN, font=("monospace", 11),
                              relief="flat", bd=3, justify="center")
        self.entry.pack(fill="x")
        self.entry.focus_set()
        self.entry.icursor("end")

        kb = tk.Frame(self, bg=BG)
        kb.pack(pady=(8, 0))

        rf1 = tk.Frame(kb, bg=BG)
        rf1.pack()
        for ch in "1234567890":
            tk.Button(rf1, text=ch, width=3, bg=BG2, fg=WHITE,
                      font=F_NORMAL, relief="flat", bd=0,
                      activebackground=BORDER, activeforeground=CYAN,
                      command=lambda c=ch: self._type(c)
            ).pack(side="left", padx=1, pady=2)

        rf2 = tk.Frame(kb, bg=BG)
        rf2.pack(pady=(2, 0))
        for ch, fg, w, cmd in [
            (".", WHITE, 4, lambda: self._type(".")),
            ("/", WHITE, 4, lambda: self._type("/")),
            ("⌫", ORANGE, 4, self._backspace),
            ("Limpiar", MUTED, 8, lambda: self.var.set("")),
        ]:
            tk.Button(rf2, text=ch, width=w, bg=BG2, fg=fg,
                      font=F_SMALL, relief="flat", bd=0,
                      activebackground=BORDER, command=cmd
            ).pack(side="left", padx=2)

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
