"""
controlador/controladorTemas.py — aplica temas recursivamente respetando roles de color
"""
import tkinter as tk
from estilo.estiloFactory import EstiloFactory
from vista.gui_dictionary import ROL_BG, ROL_BG2, ROL_CYAN, ROL_MUTED, ROL_GREEN, ROL_ORANGE, ROL_RED, ROL_BLUE, ROL_WHITE, ROL_BOTON


# Roles semánticos que se preservan al cambiar tema.
# Se asignan con: widget._color_role = "cyan" | "muted" | "green" | etc.
# Widgets sin rol reciben colorWhite() por defecto.


def _color_por_rol(estilo, rol: str) -> str:
    return getattr(estilo, rol, estilo.white)


def etiquetar(widget, bg_rol: str = ROL_BG, fg_rol: str = ROL_WHITE):
    """Asigna roles de color a un widget para que el tema lo repinte correctamente."""
    widget._bg_rol = bg_rol
    widget._fg_rol = fg_rol


class ControladorTemas:
    def __init__(self, root):
        self.root = root

    def aplicarTema(self, tipo: str):
        estilo = EstiloFactory.definirEstilo(tipo)
        try:
            self.root.master.apply_estilo(estilo)
        except Exception:
            pass
        self._aplicar_recursivo(self.root.master, estilo)
        self._aplicar_recursivo(self.root, estilo)

    def aceptarTema(self, tipo: str):
        estilo = EstiloFactory.definirEstilo(tipo)

        # Guardar en config
        try:
            self.root.master.config.theme = tipo
        except Exception:
            pass

        # Actualizar self.estilo en el dashboard para que los próximos scans
        # usen los colores correctos en dot, ping, etc.
        try:
            self.root.master.apply_estilo(estilo)
        except Exception:
            pass

        self._aplicar_recursivo(self.root.master, estilo)

    def _aplicar_recursivo(self, widget, estilo):
        bg_rol = getattr(widget, "_bg_rol", ROL_BG)
        fg_rol = getattr(widget, "_fg_rol", ROL_WHITE)

        bg_color = _color_por_rol(estilo, bg_rol)
        fg_color = _color_por_rol(estilo, fg_rol)

        # Fondo — aplica a todos
        try:
            widget.configure(bg=bg_color)
        except Exception:
            pass

        # Color de texto según tipo de widget
        if isinstance(widget, tk.Label):
            try:
                widget.configure(fg=fg_color)
            except Exception:
                pass

        elif isinstance(widget, tk.Button):
            btn_bg = _color_por_rol(estilo, getattr(widget, "_bg_rol", ROL_BOTON))
            try:
                widget.configure(
                    bg=btn_bg,
                    fg=fg_color,
                    activebackground=estilo.colorBg2(),
                    activeforeground=estilo.colorWhite()
                )
            except Exception:
                pass

        elif isinstance(widget, tk.Entry):
            try:
                widget.configure(
                    bg=estilo.colorBg2(),
                    fg=estilo.colorWhite(),
                    insertbackground=estilo.colorCyan()
                )
            except Exception:
                pass

        elif isinstance(widget, tk.OptionMenu):
            try:
                widget.configure(
                    bg=estilo.colorBg2(),
                    fg=estilo.colorWhite(),
                    activebackground=estilo.colorBg2(),
                    activeforeground=estilo.colorCyan()
                )
                # El menú interno no es hijo visible — hay que configurarlo directo
                menu = widget["menu"]
                menu.configure(
                    bg=estilo.colorBg2(),
                    fg=estilo.colorWhite(),
                    activebackground=estilo.colorBg2(),
                    activeforeground=estilo.colorCyan()
                )
            except Exception:
                pass

        elif isinstance(widget, tk.Canvas):
            try:
                widget.configure(bg=estilo.colorBg2())
            except Exception:
                pass

        elif isinstance(widget, tk.Frame):
            # Frames con rol BORDER son separadores
            if bg_rol == "border":
                try:
                    widget.configure(bg=estilo.colorBorder())
                except Exception:
                    pass

        # Recursión en hijos
        try:
            for child in widget.winfo_children():
                self._aplicar_recursivo(child, estilo)
        except Exception:
            pass