# Manual de implementación del sistema de temas — Net Monitor

## Visión general

El sistema de temas permite cambiar la paleta de colores de toda la aplicación
en tiempo real sin reiniciar. Está basado en tres capas:

1. **Estilo** — objeto que contiene los colores del tema actual
2. **Roles** — etiquetas semánticas que asignan un propósito de color a cada widget
3. **Controlador de temas** — recorre el árbol de widgets y aplica los colores correctos

---

## Archivos involucrados

```
estilo/
    estilizador.py       clase base abstracta Estilo
    dark.py              implementación tema oscuro (DarkColor)
    light.py             implementación tema claro (LightColor)
    estiloFactory.py     instancia el estilo correcto por nombre

vista/
    gui_dictionary.py    constantes ROL_*, TEMAS, CLASESTEMAS
    selectema.py         ventana de selección de tema

controlador/
    controladorTemas.py  lógica de aplicación recursiva de temas
```

---

## Cómo funciona un objeto de estilo

Cada tema es una clase que hereda de `Estilo` (abstracta) e implementa
todos sus métodos. Los atributos son los colores como strings hex:

```python
class DarkColor(Estilo):
    def __init__(self):
        self.nombre = "dark"
        self.bg     = "#0f0f12"
        self.bg2    = "#161620"
        self.border = "#1e1e2a"
        self.green  = "#3ddc84"
        self.orange = "#f0a030"
        self.red    = "#e05252"
        self.cyan   = "#7fd4c1"
        self.blue   = "#7a9fd4"
        self.white  = "#e0e0e8"
        self.muted  = "#4a4a5a"
        self.boton  = "#0f2520"
```

Los métodos `colorBg()`, `colorCyan()`, etc. simplemente retornan el atributo.
`getNombre()` retorna el string del nombre (`"dark"`, `"light"`, etc.).

---

## Agregar un tema nuevo

### 1. Crear la clase del tema

Crear `estilo/mitema.py` heredando de `Estilo` e implementando todos los métodos:

```python
from estilo.estilizador import Estilo

class MiTema(Estilo):
    def __init__(self):
        self.nombre = "mitema"
        self.bg     = "#..."
        self.bg2    = "#..."
        self.border = "#..."
        self.green  = "#..."
        self.orange = "#..."
        self.red    = "#..."
        self.cyan   = "#..."
        self.blue   = "#..."
        self.white  = "#..."
        self.muted  = "#..."
        self.boton  = "#..."

    def colorBg(self):     return self.bg
    def colorBg2(self):    return self.bg2
    def colorBorder(self): return self.border
    def colorGreen(self):  return self.green
    def colorOrange(self): return self.orange
    def colorRed(self):    return self.red
    def colorCyan(self):   return self.cyan
    def colorBlue(self):   return self.blue
    def colorWhite(self):  return self.white
    def colorMuted(self):  return self.muted
    def colorBoton(self):  return self.boton
    def getNombre(self):   return self.nombre
```

### 2. Registrar el tema en gui_dictionary.py

```python
from estilo import dark, light, mitema   # agregar import

TEMAS = {
    "Oscuro":  "dark",
    "Claro":   "light",
    "Mi Tema": "mitema",               # agregar entrada
}

CLASESTEMAS = {
    "dark":   dark.DarkColor,
    "light":  light.LightColor,
    "mitema": mitema.MiTema,           # agregar entrada
}
```

El menú desplegable en `selectema.py` lee `TEMAS.keys()` automáticamente,
así que el nuevo tema aparece sin tocar ningún otro archivo.

---

## Roles de color

Un **rol** es una etiqueta que indica qué función semántica tiene el color
de un widget. Los roles están definidos en `gui_dictionary.py`:

```python
ROL_BG     = "bg"      # fondo principal
ROL_BG2    = "bg2"     # fondo de filas y cajas
ROL_CYAN   = "cyan"    # títulos y acentos
ROL_MUTED  = "muted"   # texto secundario
ROL_GREEN  = "green"   # estado online / descarga
ROL_ORANGE = "orange"  # latencia alta
ROL_RED    = "red"     # estado offline
ROL_BLUE   = "blue"    # IPs
ROL_WHITE  = "white"   # texto principal
ROL_BOTON  = "boton"   # fondo de botones de acción
```

El controlador resuelve el color con `getattr(estilo, rol, estilo.white)`,
que equivale a `estilo.bg`, `estilo.cyan`, etc. Por eso los nombres de los
roles deben coincidir exactamente con los atributos del objeto estilo.

---

## Etiquetar un widget

Para que el controlador sepa qué color aplicar al cambiar de tema,
hay que asignar un rol a cada widget con `etiquetar()`:

```python
from controlador.controladorTemas import etiquetar, ROL_BG, ROL_CYAN

lbl = tk.Label(parent, text="Hola", bg=estilo.bg, fg=estilo.cyan)
etiquetar(lbl, ROL_BG, ROL_CYAN)
```

`etiquetar(widget, bg_rol, fg_rol)` asigna:
- `widget._bg_rol` — rol del fondo
- `widget._fg_rol` — rol del texto

Los frames separadores usan asignación directa:

```python
sep = tk.Frame(parent, bg=estilo.border, height=1)
sep._bg_rol = "border"
```

### Widgets sin etiquetar

Si un widget no tiene `_bg_rol` ni `_fg_rol`, el controlador usa `ROL_BG`
para el fondo y `ROL_WHITE` para el texto como valores por defecto.

### Roles semánticos en tiempo real

Algunos widgets cambian de rol según el estado del programa. Por ejemplo,
el ping puede ser verde, naranja o rojo según la latencia. En ese caso
hay que actualizar el rol manualmente al cambiar el estado:

```python
row["ping"].config(fg=self.estilo.red)
row["ping"]._fg_rol = "red"    # actualizar el rol para el próximo cambio de tema
```

Sin esta línea, el próximo cambio de tema pintaría el widget con el rol
anterior, ignorando su estado actual.

---

## Cómo se aplica un tema

### aplicarTema(tipo) — preview sin guardar

```python
controladorTema.aplicarTema("light")
```

1. Instancia el estilo del tipo dado
2. Llama `dashboard.apply_estilo(estilo)` para actualizar `self.estilo`
   (así los próximos scans usan los colores del preview)
3. Recorre recursivamente todos los widgets del dashboard y del selector

### aceptarTema(tipo) — guardar y aplicar

```python
controladorTema.aceptarTema("light")
```

1. Instancia el estilo
2. Guarda `config.theme = tipo` (persiste en `config.json`)
3. Llama `dashboard.apply_estilo(estilo)`
4. Recorre recursivamente todos los widgets del dashboard

---

## Crear una vista nueva con soporte de temas

### 1. Recibir el estilo como parámetro

```python
class MiVista(tk.Toplevel):
    def __init__(self, parent, estilo):
        super().__init__(parent)
        self.estilo = estilo
        self.configure(bg=self.estilo.bg)
        self._build()
```

### 2. Usar el estilo al crear widgets y etiquetarlos

```python
def _build(self):
    lbl = tk.Label(self, text="Título",
                   bg=self.estilo.bg, fg=self.estilo.cyan,
                   font=F_TITLE)
    etiquetar(lbl, ROL_BG, ROL_CYAN)
    lbl.pack()
```

### 3. Obtener el estilo actual al abrir la vista

En el dashboard, siempre obtener el estilo actual antes de abrir una vista:

```python
def _open_mi_vista(self):
    estilo = EstiloFactory.definirEstilo(self.config.theme)
    MiVista(self, estilo)
```

Esto asegura que la nueva vista se abra con el tema activo en ese momento,
no con el del arranque de la aplicación.

---

## Reglas de oro

- Siempre etiquetar todos los widgets con `etiquetar()` o asignar `_bg_rol` directamente
- Actualizar `_fg_rol` manualmente cuando el estado semántico de un widget cambia
- Nunca hardcodear colores hex en widgets — siempre usar `self.estilo.cyan`, etc.
- Al abrir cualquier diálogo, obtener el estilo con `EstiloFactory.definirEstilo(self.config.theme)`
- Los teclados (`VirtualKeyboard`, `Numpad`) reciben `estilo` como primer argumento
