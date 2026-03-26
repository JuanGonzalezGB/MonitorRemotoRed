"""
view/keyboards.py — widgets de teclado virtual reutilizables
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


class VirtualKeyboard(tk.Frame):
    """Teclado QWERTY para texto libre."""

    KEYS = [
        list("1234567890"),
        list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm-_"),
    ]

    def __init__(self, parent, entry: tk.Entry, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._entry = entry
        self._uppercase = False
        self._build()

    def _build(self):
        for row in self.KEYS:
            rf = tk.Frame(self, bg=BG)
            rf.pack()
            for ch in row:
                tk.Button(rf, text=ch, width=3, bg=BG2, fg=WHITE,
                          font=F_SMALL, relief="flat", bd=0,
                          activebackground=BORDER, activeforeground=CYAN,
                          command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        sp = tk.Frame(self, bg=BG)
        sp.pack(pady=(2, 0))
        self._btn_case = tk.Button(sp, text="abc", width=4, bg=BG2, fg=MUTED,
                                   font=F_SMALL, relief="flat", bd=0,
                                   command=self._toggle_case)
        self._btn_case.pack(side="left", padx=1)
        tk.Button(sp, text="espacio", width=8, bg=BG2, fg=WHITE,
                  font=F_SMALL, relief="flat", bd=0,
                  command=lambda: self._type(" ")).pack(side="left", padx=1)
        tk.Button(sp, text="⌫", width=4, bg=BG2, fg=ORANGE,
                  font=F_SMALL, relief="flat", bd=0,
                  command=self._backspace).pack(side="left", padx=1)

    def _type(self, ch: str):
        ch = ch.upper() if self._uppercase else ch
        pos = self._entry.index("insert")
        var = self._entry.cget("textvariable")
        sv = self._entry.nametowidget(self._entry.winfo_parent())
        # Operar directo sobre el widget Entry
        self._entry.insert(pos, ch)

    def _backspace(self):
        pos = self._entry.index("insert")
        if pos > 0:
            self._entry.delete(pos - 1, pos)

    def _toggle_case(self):
        self._uppercase = not self._uppercase
        self._btn_case.config(text="ABC" if self._uppercase else "abc")


class Numpad(tk.Frame):
    """Teclado numérico para IPs y subredes."""

    def __init__(self, parent, entry: tk.Entry, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._entry = entry
        self._build()

    def _build(self):
        rf1 = tk.Frame(self, bg=BG)
        rf1.pack()
        for ch in "1234567890":
            tk.Button(rf1, text=ch, width=3, bg=BG2, fg=WHITE,
                      font=F_NORMAL, relief="flat", bd=0,
                      activebackground=BORDER, activeforeground=CYAN,
                      command=lambda c=ch: self._type(c)
            ).pack(side="left", padx=1, pady=2)

        rf2 = tk.Frame(self, bg=BG)
        rf2.pack(pady=(2, 0))
        for ch, fg, w, cmd in [
            (".", WHITE, 4, lambda: self._type(".")),
            ("/", WHITE, 4, lambda: self._type("/")),
            ("⌫", ORANGE, 4, self._backspace),
            ("Limpiar", MUTED, 8, lambda: self._entry.delete(0, "end")),
        ]:
            tk.Button(rf2, text=ch, width=w, bg=BG2, fg=fg,
                      font=F_SMALL, relief="flat", bd=0,
                      activebackground=BORDER, command=cmd
            ).pack(side="left", padx=2)

    def _type(self, ch: str):
        pos = self._entry.index("insert")
        self._entry.insert(pos, ch)

    def _backspace(self):
        pos = self._entry.index("insert")
        if pos > 0:
            self._entry.delete(pos - 1, pos)
