# Monitor Red — rama servicios (Linux)

El monitor de red lee los dispositivos detectados por el servicio `network-collector`, el cual escanea la red de forma continua e independiente a si la interfaz gráfica está abierta o no. La GUI solo lee y visualiza — no ejecuta scans directamente.

---

## Dependencias

### Python

```bash
pip3 install -r reqlinux.txt
```

### Speedtest

también puede instalar el speedtest de ookla para realizar speedtest en segundo plano que se verá reflejado en speed panel
```bash
sudo apt-get install curl
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest
```

### rpi-core

Este programa forma parte de un ecosistema de aplicaciones que comparten la librería `rpi-core`. Dicha librería provee utilidades comunes (widgets, estilos, acceso a base de datos, configuración compartida) y es instalada como dependencia editable:

```bash
pip install -e /ruta/a/rpi-core
```

`rpi-core` también contiene el archivo `.env` con la configuración compartida del ecosistema, incluyendo la conexión a MongoDB y el intervalo de scan del servicio. Asegúrese de que este archivo exista y esté correctamente configurado antes de ejecutar el programa.

### Servicio network-collector

Esta rama requiere que el servicio `network-collector` esté corriendo en el sistema. Es el encargado de escanear la red periódicamente usando `arp-scan` y persistir los resultados en MongoDB. La GUI depende de él para tener datos — sin el servicio activo, la lista de dispositivos aparecerá vacía.

```bash
sudo apt install arp-scan
```

Instalar el servicio:

```bash
sudo cp network-collector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable network-collector
sudo systemctl start network-collector
```

### MongoDB

MongoDB es **requerido** en esta rama. El servicio escribe en `scanner.scans` y la GUI lee de ahí. Sin MongoDB el programa no funciona.

```bash
sudo apt install mongodb
```

---

## Base de datos

El programa usa dos colecciones dentro de la base de datos `scanner`:

- `scanner.scans` — escrita exclusivamente por el servicio `network-collector`. Contiene el historial de dispositivos detectados con MAC, IP, vendor y ping. No debe ser modificada manualmente.
- `scanner.dispositivos` — escrita exclusivamente por esta GUI. Contiene los nombres personalizados asociados a cada MAC. Es leída también por otras apps del ecosistema (ej: pihole-monitor).

Puede configurar la IP, credenciales y nombre de la base de datos desde la configuración del programa (ícono ⚙) o editando `config.json`, el cual se creará en la primera ejecución.

---

## Intervalo de scan

El intervalo de scan se controla desde la configuración del programa. Al cambiar este valor se actualiza automáticamente `SCAN_INTERVAL_S` en el `.env` de `rpi-core` y se reinicia `network-collector` para aplicar el nuevo intervalo.

Para que el reinicio del servicio funcione sin contraseña, agregue esta regla:

```bash
sudo visudo -f /etc/sudoers.d/network-collector
```

```
tuusuario ALL=(ALL) NOPASSWD: /bin/systemctl restart network-collector
```

> **Nota:** La ruta al `.env` de `rpi-core` está definida en `main.py` como `_ENV_PATH`. Si instala el programa en un sistema distinto, asegúrese de actualizar esta ruta antes de ejecutar o compilar.

---

## Comportamiento

- La lista muestra **todos los dispositivos** que el servicio ha detectado alguna vez, marcando como offline los que no se han visto en los últimos 5 minutos.
- El botón **Scan** refresca la lectura desde MongoDB de forma inmediata.
- Los dispositivos pueden **renombrarse** haciendo clic en su nombre. El nombre queda asociado a la MAC y persiste entre sesiones.
- Los dispositivos pueden **eliminarse** desde el mismo diálogo de renombrado (ícono 🗑). Se puede eliminar solo el nombre guardado, o también el registro completo de `scanner.scans`.

---

## Compilar con PyInstaller

> **Atención:** Antes de compilar, verifique que `_ENV_PATH` en `main.py` apunta a la ubicación correcta del `.env` de `rpi-core` en el sistema destino.

```bash
pyinstaller --onedir \
  --hidden-import pymongo \
  --hidden-import pymongo.mongo_client \
  --hidden-import pymongo.collection \
  --hidden-import bson \
  --hidden-import bson.codec_options \
  --name="Net Monitor" main.py
```

---

## Ecosistema

Este programa es parte de un conjunto de aplicaciones construidas sobre `rpi-core`:

- **network-collector** — servicio que escanea la red y persiste dispositivos en MongoDB.
- **network-monitor** — esta aplicación. Visualiza los dispositivos detectados por el servicio.
- **pihole-monitor** — monitorea estadísticas de Pi-hole. Lee `scanner.dispositivos` para mostrar nombres de dispositivos.

La intención es que todas las apps del ecosistema migren progresivamente a usar las librerías y widgets de `rpi-core` como base común.

---

*Este proyecto incluye código generado con asistencia de herramientas de IA, manualmente revisado y modificado por el autor.*
