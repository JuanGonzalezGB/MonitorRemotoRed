# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Juan S.G. Castellanos

"""
vista/keyboards.py — widgets de teclado virtual reutilizables
"""
import tkinter as tk
from vista.gui_dictionary import FORMATS

F_NORMAL = FORMATS["F_NORMAL"]
F_SMALL  = FORMATS["F_SMALL"]


class VirtualKeyboard(tk.Frame):
    """Teclado QWERTY con alternancia a teclado de símbolos."""

    KEYS = [
        list("1234567890"),
        list("qwertyuiop"),
        list("asdfghjklñ"),
        list("zxcvbnm.-_"),
    ]

    def __init__(self, estilo, parent, entry: tk.Entry, **kwargs):
        self.estilo = estilo
        super().__init__(parent,bg=self.estilo.bg,  **kwargs)
        self._entry = entry
        self._uppercase = False
        self._char_kb = None
        self._build()

    def _build(self):
        for row in self.KEYS:
            rf = tk.Frame(self, bg=self.estilo.bg)
            rf.pack()
            for ch in row:
                tk.Button(
                    rf, text=ch, width=3,
                    bg=self.estilo.bg2, fg=self.estilo.white,
                    font=F_SMALL, relief="flat", bd=0,
                    activebackground=self.estilo.border,
                    activeforeground=self.estilo.cyan,
                    command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        sp = tk.Frame(self, bg=self.estilo.bg)
        sp.pack(pady=(2, 0))

        self._btn_case = tk.Button(
            sp, text="abc", width=4,
            bg=self.estilo.bg2, fg=self.estilo.muted,
            font=F_SMALL, relief="flat", bd=0,
            command=self._toggle_case
        )
        self._btn_case.pack(side="left", padx=1)

        tk.Button(
            sp, text="#@", width=4,
            bg=self.estilo.bg2, fg=self.estilo.cyan,
            font=F_SMALL, relief="flat", bd=0,
            command=self._toggle_symbols
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="espacio", width=16,
            bg=self.estilo.bg2, fg=self.estilo.white,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type(" ")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌫", width=4,
            bg=self.estilo.bg2, fg=self.estilo.orange,
            font=F_SMALL, relief="flat", bd=0,
            command=self._backspace
        ).pack(side="left", padx=1)

    def _type(self, ch: str):
        ch = ch.upper() if self._uppercase else ch
        pos = self._entry.index("insert")
        self._entry.insert(pos, ch)

    def _backspace(self):
        pos = self._entry.index("insert")
        if pos > 0:
            self._entry.delete(pos - 1, pos)

    def _toggle_case(self):
        self._uppercase = not self._uppercase
        self._btn_case.config(text="ABC" if self._uppercase else "abc")

    def _toggle_symbols(self):
        # Ocultar QWERTY y mostrar símbolos en el mismo contenedor padre
        self.pack_forget()
        if self._char_kb is None:
            self._char_kb = CharKeyboard(
                self.estilo, self.master, self._entry,
                on_back=self._show_qwerty
            )
        self._char_kb.pack(pady=(8, 0), padx=8)

    def _show_qwerty(self):
        if self._char_kb:
            self._char_kb.pack_forget()
        self.pack(pady=(8, 0), padx=8)


class CharKeyboard(tk.Frame):
    """Teclado de símbolos y caracteres especiales."""

    KEYS = [
        list("!@#$%^&*()"),
        list("[]{}<>/\\|"),
        list("+=~`.:,;"),
        list("\"'¿?-_"),
    ]

    def __init__(self, estilo, parent, entry: tk.Entry,
                 on_back=None, **kwargs):
        self.estilo = estilo
        super().__init__(parent, bg=self.estilo.bg, **kwargs)
        self._entry = entry
        self._on_back = on_back
        self._build()

    def _build(self):
        for row in self.KEYS:
            rf = tk.Frame(self, bg=self.estilo.bg)
            rf.pack()
            for ch in row:
                tk.Button(
                    rf, text=ch, width=3,
                    bg=self.estilo.bg2, fg=self.estilo.white,
                    font=F_SMALL, relief="flat", bd=0,
                    activebackground=self.estilo.border,
                    activeforeground=self.estilo.cyan,
                    command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        sp = tk.Frame(self, bg=self.estilo.bg)
        sp.pack(pady=(2, 0))

        tk.Button(
            sp, text="abc", width=4,
            bg=self.estilo.bg2, fg=self.estilo.cyan,
            font=F_SMALL, relief="flat", bd=0,
            command=self._back
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="espacio", width=16,
            bg=self.estilo.bg2, fg=self.estilo.white,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type(" ")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌫", width=4,
            bg=self.estilo.bg2, fg=self.estilo.orange,
            font=F_SMALL, relief="flat", bd=0,
            command=self._backspace
        ).pack(side="left", padx=1)

    def _type(self, ch: str):
        pos = self._entry.index("insert")
        self._entry.insert(pos, ch)

    def _backspace(self):
        pos = self._entry.index("insert")
        if pos > 0:
            self._entry.delete(pos - 1, pos)

    def _back(self):
        if self._on_back:
            self._on_back()


class Numpad(tk.Frame):
    """Teclado numérico para IPs, puertos y subredes."""

    def __init__(self, estilo, parent, entry: tk.Entry, **kwargs):
        self.estilo = estilo
        super().__init__(parent, bg=self.estilo.bg, **kwargs)
        self._entry = entry
        self._build()

    def _build(self):
        rf1 = tk.Frame(self, bg=self.estilo.bg)
        rf1.pack()
        for ch in "1234567890":
            tk.Button(
                rf1, text=ch, width=2,
                bg=self.estilo.bg2, fg=self.estilo.white,
                font=F_NORMAL, relief="flat", bd=0,
                activebackground=self.estilo.border,
                activeforeground=self.estilo.cyan,
                command=lambda c=ch: self._type(c)
            ).pack(side="left", padx=1, pady=2)

        rf2 = tk.Frame(self, bg=self.estilo.bg)
        rf2.pack(pady=(2, 0))
        for ch, fg, w, cmd in [
            (".", self.estilo.white,  3, lambda: self._type(".")),
            ("/", self.estilo.white,  3, lambda: self._type("/")),
            (":", self.estilo.white,  3, lambda: self._type(":")),
            ("⌫", self.estilo.orange, 3, self._backspace),
            ("Limpiar", self.estilo.muted, 8, lambda: self._entry.delete(0, "end")),
        ]:
            tk.Button(
                rf2, text=ch, width=w,
                bg=self.estilo.bg2, fg=fg,
                font=F_SMALL, relief="flat", bd=0,
                activebackground=self.estilo.border,
                command=cmd
            ).pack(side="left", padx=2)

    def _type(self, ch: str):
        pos = self._entry.index("insert")
        self._entry.insert(pos, ch)

    def _backspace(self):
        pos = self._entry.index("insert")
        if pos > 0:
            self._entry.delete(pos - 1, pos)
