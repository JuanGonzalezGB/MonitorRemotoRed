# Manual de implementación del sistema de temas

## Visión general

El sistema permite cambiar la paleta de colores de toda la aplicación
en tiempo de ejecución sin reiniciar. Está diseñado para ser portable —
puede copiarse a cualquier proyecto tkinter con mínimas adaptaciones.

Está compuesto por tres capas independientes:

```
Estilo      — objeto con los colores del tema activo
Roles       — etiquetas semánticas en cada widget que indican qué color usar
Controlador — recorre el árbol de widgets y aplica los colores del nuevo tema
```

Y tres archivos de soporte:

```
EstiloFactory  — instancia el objeto correcto dado un nombre de tema
gui_dictionary — registro central de temas disponibles
config.py      — persiste el tema activo en config.json
```

---

## Estructura de archivos mínima

Para portar el sistema a otro proyecto, estos son los archivos necesarios:

```
mi_proyecto/
├── estilo/
│   ├── __init__.py
│   ├── estilizador.py      ← clase base abstracta (copiar tal cual)
│   ├── dark.py             ← tema oscuro (copiar o adaptar colores)
│   └── estiloFactory.py    ← instancia temas por nombre (copiar tal cual)
├── controlador/
│   ├── __init__.py
│   └── controladorTemas.py ← lógica de retematización (copiar tal cual)
├── modelo/
│   ├── __init__.py
│   └── config.py           ← persistencia en config.json (copiar o adaptar)
└── vista/
    └── gui_dictionary.py   ← registro de temas y fuentes (adaptar)
```

Los archivos marcados "copiar tal cual" no necesitan modificarse entre
proyectos. Solo hay que adaptar `gui_dictionary.py` con los temas propios
y `config.py` si el proyecto ya tiene su propio sistema de configuración.

---

## Paso 1 — Copiar los archivos base

Copiar sin modificar:

- `estilo/estilizador.py` — define la clase abstracta `Estilo`
- `estilo/estiloFactory.py` — lee `CLASESTEMAS` de `gui_dictionary` e
  instancia la clase correcta
- `controlador/controladorTemas.py` — contiene `etiquetar()`,
  `ControladorTemas` y los roles `ROL_*`
- `modelo/config.py` — lee y escribe `config.json`; expone
  `get_tema()` y `set_tema()`

---

## Paso 2 — Crear los temas

Cada tema es una clase que hereda de `Estilo` y define los atributos de
color. Los atributos deben llamarse exactamente igual en todos los temas
porque el controlador los resuelve con `getattr(estilo, rol)`.

```python
# estilo/dark.py
from estilo.estilizador import Estilo

class DarkColor(Estilo):
    def __init__(self):
        self.nombre = "dark"
        self.bg     = "#0f0f12"   # fondo principal
        self.bg2    = "#161620"   # fondo de paneles y cajas
        self.border = "#1e1e2a"   # separadores y bordes
        self.green  = "#3ddc84"   # estado positivo
        self.orange = "#f0a030"   # advertencia
        self.red    = "#e05252"   # error / estado negativo
        self.cyan   = "#7fd4c1"   # acentos y títulos
        self.blue   = "#7a9fd4"   # datos secundarios
        self.white  = "#e0e0e8"   # texto principal
        self.muted  = "#4a4a5a"   # texto secundario
        self.boton  = "#0f2520"   # fondo de botones de acción

    # Los métodos colorXxx() son requeridos por la clase abstracta.
    # Simplemente retornan el atributo correspondiente.
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

Para agregar un tema claro, crear `estilo/light.py` con la misma
estructura y colores distintos. El nombre del archivo y la clase pueden
ser cualquier cosa — lo que importa es el valor de `self.nombre` y el
registro en `gui_dictionary.py`.

---

## Paso 3 — Registrar los temas en gui_dictionary.py

`gui_dictionary.py` es el único archivo que sabe qué temas existen.
`EstiloFactory` y el selector de temas lo leen para saber qué instanciar
y qué mostrar en el dropdown.

```python
# vista/gui_dictionary.py
from estilo.dark import DarkColor
from estilo.light import LightColor   # importar cada tema nuevo

# Nombre visible en el dropdown → código interno
TEMAS: dict[str, str] = {
    "Oscuro": "dark",
    "Claro":  "light",
}

# Código interno → clase del tema
CLASESTEMAS: dict = {
    "dark":  DarkColor,
    "light": LightColor,
}
```

Agregar un tema nuevo solo requiere crear la clase, importarla aquí y
añadir dos entradas — una en `TEMAS` y una en `CLASESTEMAS`. Ningún otro
archivo necesita cambiar.

---

## Paso 4 — Adaptar la clase principal de la app

La clase principal de la app (el equivalente a `MonitorApp`) debe cumplir
un contrato mínimo para que `ControladorTemas` funcione. Necesita exponer
tres atributos y un método:

```python
class MiApp:
    def __init__(self, estilo):
        self.estilo      = estilo      # objeto Estilo activo
        self.root        = tk.Tk()     # ventana raíz
        self._ttk_style  = ttk.Style() # instancia de ttk.Style

        self.root.configure(bg=estilo.bg)
        self._ttk_style.theme_use("default")

        self._build_ui()

        # Instanciar el controlador DESPUÉS de construir la UI
        self._controlador_temas = ControladorTemas(self)

    def apply_estilo(self, nuevo_estilo) -> None:
        """
        Callback obligatorio — llamado por ControladorTemas antes de
        recorrer el árbol de widgets.
        Debe actualizar self.estilo y el bg de la ventana raíz.
        Si la app tiene referencias internas a colores (ej: listas
        dinámicas, canvas), actualizarlas aquí también.
        """
        self.estilo = nuevo_estilo
        self.root.configure(bg=nuevo_estilo.bg)
```

**Por qué después de `_build_ui()`:** `ControladorTemas.__init__` no hace
nada con los widgets todavía — solo guarda la referencia a `app`. Pero si
se instancia antes de que existan los widgets, cualquier llamada inmediata
a `aplicarTema` fallaría al intentar recorrer un árbol vacío.

---

## Paso 5 — Etiquetar los widgets

Para que el controlador sepa qué color aplicar a cada widget al cambiar
de tema, hay que estampar roles semánticos usando `etiquetar()`.

```python
from controlador.controladorTemas import etiquetar, ROL_BG, ROL_CYAN

lbl = tk.Label(parent, bg=estilo.bg, fg=estilo.cyan, text="Título")
etiquetar(lbl, ROL_BG, ROL_CYAN)
```

`etiquetar(widget, bg_rol, fg_rol)` asigna:
- `widget._bg_rol` — nombre del atributo de estilo que se usará como `bg`
- `widget._fg_rol` — nombre del atributo de estilo que se usará como `fg`

El controlador los lee con `getattr(estilo, rol)` — por eso los valores
de `ROL_*` son strings que coinciden exactamente con los atributos del
objeto estilo (`"bg"`, `"cyan"`, etc.).

### Frames y separadores

Los frames solo tienen `bg`, no `fg`. Pasar solo el primer argumento:

```python
frame = tk.Frame(parent, bg=estilo.bg)
etiquetar(frame, ROL_BG)          # sin fg_rol
```

Los separadores se etiquetan directamente sin `etiquetar()`:

```python
sep = tk.Frame(parent, bg=estilo.border, height=1)
sep._bg_rol = "border"
```

### Botones

Los botones tienen `bg/fg` y también `activebackground/activeforeground`.
`etiquetar()` es suficiente — el controlador sincroniza automáticamente
los colores activos con los mismos roles:

```python
btn = tk.Button(parent, bg=estilo.bg, fg=estilo.muted, ...)
etiquetar(btn, ROL_BG, ROL_MUTED)
# El controlador aplica bg=estilo.bg y activebackground=estilo.bg
# al mismo tiempo, sin código extra.
```

### Roles disponibles

Todos están definidos en `controladorTemas.py` como constantes:

```python
ROL_BG     = "bg"      # fondo principal
ROL_BG2    = "bg2"     # fondo de paneles y cajas
ROL_BORDER = "border"  # separadores
ROL_GREEN  = "green"   # estado positivo
ROL_ORANGE = "orange"  # advertencia
ROL_RED    = "red"     # error
ROL_CYAN   = "cyan"    # títulos y acentos
ROL_BLUE   = "blue"    # datos secundarios
ROL_WHITE  = "white"   # texto principal
ROL_MUTED  = "muted"   # texto secundario
ROL_BOTON  = "boton"   # fondo de botones de acción
```

Para agregar un rol nuevo, añadir la constante en `controladorTemas.py`
y el atributo correspondiente en todas las clases de tema.

---

## Paso 6 — Widgets con color dinámico

Algunos widgets cambian de color según el estado del programa en tiempo
de ejecución (ej: un label que se pone rojo si hay un error, verde si
todo está bien). Si solo se llama a `.config(fg=...)` sin actualizar el
rol, el próximo cambio de tema sobrescribirá el color con el rol original,
ignorando el estado actual.

La solución es actualizar `_fg_rol` junto con el color cada vez que
el estado cambia:

```python
def _set_estado(self, estado: str):
    if estado == "ok":
        self.lbl_estado.config(fg=self.estilo.green)
        self.lbl_estado._fg_rol = "green"    # ← rol actualizado
    elif estado == "error":
        self.lbl_estado.config(fg=self.estilo.red)
        self.lbl_estado._fg_rol = "red"      # ← rol actualizado
```

Sin la línea `_fg_rol = ...`, al cambiar de tema el controlador usaría
el rol con el que se creó el widget originalmente, perdiendo el estado visual.

---

## Paso 7 — Arrancar la app con el tema guardado

En `main.py`, leer el tema desde `config.json` antes de construir la UI
e inyectarlo como parámetro:

```python
# main.py
from modelo.config import get_tema
from estilo.estiloFactory import EstiloFactory
from vista.app import MiApp

def main():
    tema = get_tema()                        # lee config.json, default "dark"
    estilo = EstiloFactory.definirEstilo(tema)
    MiApp(estilo).run()

if __name__ == "__main__":
    main()
```

`EstiloFactory.definirEstilo(tipo)` busca `tipo` en `CLASESTEMAS` de
`gui_dictionary.py` e instancia la clase correspondiente. Si el código
no existe, usa `DarkColor` como fallback.

---

## Paso 8 — Abrir diálogos con el tema activo

Al abrir cualquier `Toplevel`, obtener el estilo actual desde la factory
en lugar de pasarlo desde `__init__`. Esto garantiza que si el usuario
cambió de tema después del arranque, el diálogo se abra con el tema
correcto y no con el del arranque:

```python
# En MiApp o en cualquier vista que abra un diálogo
def _open_mi_dialogo(self):
    from estilo.estiloFactory import EstiloFactory
    from modelo.config import get_tema
    estilo = EstiloFactory.definirEstilo(get_tema())
    MiDialogo(self.root, estilo)
```

El diálogo recibe `estilo` como argumento, lo usa para construir su UI
y lo pasa a `etiquetar()` en cada widget:

```python
class MiDialogo(tk.Toplevel):
    def __init__(self, parent, estilo):
        super().__init__(parent)
        self.estilo = estilo
        self.configure(bg=estilo.bg)
        self._build_ui()

    def _build_ui(self):
        lbl = tk.Label(self, bg=self.estilo.bg, fg=self.estilo.cyan,
                       text="Título")
        etiquetar(lbl, ROL_BG, ROL_CYAN)
        lbl.pack()
```

---

## Paso 9 — Widgets ttk (barras de progreso, etc.)

Los widgets `ttk` no participan del sistema de roles — tienen su propio
sistema de estilos. Hay que actualizarlos manualmente en `_retemar_ttk()`
dentro de `ControladorTemas`:

```python
def _retemar_ttk(self, estilo) -> None:
    s = self._app._ttk_style
    s.configure("Green.Horizontal.TProgressbar",
                troughcolor=estilo.bg2, background=estilo.green)
    s.configure("Orange.Horizontal.TProgressbar",
                troughcolor=estilo.bg2, background=estilo.orange)
    s.configure("Red.Horizontal.TProgressbar",
                troughcolor=estilo.bg2, background=estilo.red)
```

Si el proyecto no usa barras de progreso ttk, este método puede quedar
vacío o eliminarse.

---

## Paso 10 — Selector de temas (opcional)

El archivo `vista/selectema.py` provee una ventana `Toplevel` lista para
usar. Lee `TEMAS` de `gui_dictionary.py` para poblar el dropdown y usa
`ControladorTemas` para preview en vivo y persistencia.

Para integrarlo en cualquier app, basta con llamarlo desde un botón:

```python
def _open_theme_selector(self):
    from vista.selectema import ThemeSelector
    ThemeSelector(self.root, self)
```

`ThemeSelector` espera que `app` (el segundo argumento) exponga:
- `app.estilo` — estilo actual
- `app._controlador_temas` — instancia de `ControladorTemas`
- `app.apply_estilo(estilo)` — callback de actualización

---

## Referencia rápida — checklist de portabilidad

Al llevar el sistema a un proyecto nuevo, verificar cada punto:

```
[ ] estilo/estilizador.py copiado sin cambios
[ ] estilo/estiloFactory.py copiado sin cambios
[ ] controlador/controladorTemas.py copiado sin cambios
[ ] modelo/config.py copiado o adaptado
[ ] Al menos un tema creado en estilo/dark.py (u otro nombre)
[ ] gui_dictionary.py con TEMAS y CLASESTEMAS poblados
[ ] Clase principal expone: .root, .estilo, ._ttk_style, .apply_estilo()
[ ] ControladorTemas instanciado DESPUÉS de _build_ui()
[ ] Todos los widgets etiquetados con etiquetar() o ._bg_rol directo
[ ] Widgets con color dinámico actualizan ._fg_rol junto al .config(fg=...)
[ ] main.py lee el tema con get_tema() antes de construir la UI
[ ] Diálogos obtienen el estilo con EstiloFactory.definirEstilo(get_tema())
```

---

## Resumen de reglas

- Nunca hardcodear colores hex en widgets — siempre usar `estilo.cyan`, etc.
- Etiquetar todos los widgets con `etiquetar()` o `._bg_rol` directamente
- Actualizar `._fg_rol` cuando el color de un widget cambia por estado
- Instanciar `ControladorTemas` después de construir la UI, nunca antes
- Abrir diálogos obteniendo el estilo fresco con `EstiloFactory + get_tema()`
- Los nombres de los roles (`ROL_*`) deben coincidir con los atributos de `Estilo`
- `_retemar_ttk()` es el único lugar donde se actualizan widgets ttk
