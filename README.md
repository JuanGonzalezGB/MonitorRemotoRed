# Monitor Red — rama servicios (Linux)

El monitor de red lee los dispositivos detectados por el servicio `network-collector`, el cual escanea la red de forma continua e independiente a si la interfaz gráfica está abierta o no. La GUI solo lee y visualiza — no ejecuta scans directamente.

---

## Requisitos

### Dependencias Python

```bash
pip3 install -r reqlinux.txt
```

### Servicio network-collector

Esta rama requiere que el servicio `network-collector` esté corriendo en el sistema. El servicio usa `arp-scan` para detectar dispositivos en la red y persiste los resultados en MongoDB.

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

El intervalo de scan se controla desde la configuración del programa. Al cambiar este valor se actualiza automáticamente el `.env` del servicio y se reinicia `network-collector` para aplicar el nuevo intervalo.

Para que el reinicio del servicio funcione sin contraseña, agregue esta regla:

```bash
sudo visudo -f /etc/sudoers.d/network-collector
```

```
tuusuario ALL=(ALL) NOPASSWD: /bin/systemctl restart network-collector
```

---

## Comportamiento

- La lista muestra **todos los dispositivos** que el servicio ha detectado alguna vez, marcando como offline los que no se han visto en los últimos 5 minutos.
- El botón **Scan** refresca la lectura desde MongoDB de forma inmediata.
- Los dispositivos pueden **renombrarse** haciendo clic en su nombre. El nombre queda asociado a la MAC y persiste entre sesiones.
- Los dispositivos pueden **eliminarse** desde el mismo diálogo de renombrado (ícono 🗑). Se puede eliminar solo el nombre guardado, o también el registro completo de `scanner.scans`.

---

## Compilar con PyInstaller

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

*Este proyecto incluye código generado con asistencia de herramientas de IA, manualmente revisado y modificado por el autor.*
