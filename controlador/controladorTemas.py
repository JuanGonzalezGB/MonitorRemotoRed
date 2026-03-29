import tkinter as tk
from estilo.estiloFactory import EstiloFactory


class ControladorTemas:
    def __init__(self, root):
        self.root = root

    def aplicarTema(self, tipo):
        estilo = EstiloFactory.definirEstilo(tipo)

        self._aplicar_recursivo(self.root, estilo)

    def _aplicar_recursivo(self, widget, estilo):

        # --- fondo ---
        try:
            widget.configure(bg=estilo.colorBg())
        except:
            pass

        # --- labels ---
        if isinstance(widget, tk.Label):
            widget.config(
                bg=estilo.colorBg(),
                fg=estilo.colorWhite()
            )

        # --- botones ---
        elif isinstance(widget, tk.Button):
            widget.config(
                bg=estilo.colorBoton(),
                fg=estilo.colorCyan(),
                activebackground=estilo.colorBg2(),
                activeforeground=estilo.colorWhite()
            )

        # --- option menu ---
        elif isinstance(widget, tk.OptionMenu):
            widget.config(
                bg=estilo.colorBg2(),
                fg=estilo.colorWhite(),
                activebackground=estilo.colorBg2()
            )

        # Entry 
        elif isinstance(widget, tk.Entry):
            widget.config(
                bg=estilo.colorBg2(),
                fg=estilo.colorWhite(),
                insertbackground=estilo.colorWhite
            )

        for child in widget.winfo_children():
            self._aplicar_recursivo(child, estilo)

        # --- labels ---
        if isinstance(widget, tk.Label):
            fg = widget.cget("fg")

            if fg == self.root.master.estilo.cyan:
                new_fg = estilo.colorCyan()
            elif fg == self.root.master.estilo.muted:
                new_fg = estilo.colorMuted()
            elif fg == self.root.master.estilo.blue:
                new_fg = estilo.colorBlue()
            else:
                new_fg = estilo.colorWhite()

            widget.config(bg=widget.cget("bg"), fg=new_fg)

        # --- botones ---
        elif isinstance(widget, tk.Button):
            widget.config(
                bg=estilo.colorBoton(),
                fg=estilo.colorCyan()
            )

        # --- option menu ---
        elif isinstance(widget, tk.OptionMenu):
            widget.config(
                bg=estilo.colorBg2(),
                fg=estilo.colorWhite()
            )

        for child in widget.winfo_children():
            self._aplicar_recursivo(child, estilo)

    def aceptarTema(self, tipo):
        self.root.master.config.theme = tipo

        self._aplicar_recursivo(self.root.master, EstiloFactory.definirEstilo(tipo))          