#Monitor Red(LINUX/WINDOWS)
-----------------------------

#Instalar requisitos LINUX:

     pip3 install -r reqlinux.txt

-----------------------------

#Instalar requisitos WINDOWS:

descargue nmap: https://nmap.org/ o:

     winget install nmap

luego:

     pip3 install -r reqwin.txt

-----------------------------

#uso de mongodb es opcional. 

El programa está pensado para usar una base de datos mongodb para almacenar los dispositivos que se conecten a la red, sin embargo, de no haber una base de datos mongodb corriendo en localhost o en la red local, el programa guardará los dispositivos en 'devices.json', si luego decide instalar mongodb y hacer uso de esta para el programa, el programa migrará la información del JSON a su base de datos y se eliminará del sistema.

Puede configurar ip, credenciales y nombre de la base de datos que quiere usar desde el programa o editando 'settings.json' el cual se creará en la primera ejecución del programa, también puede cambiar defaults en config.py para que este se cree con la configuración deseada.

-----------------------------
#OPCIONAL

Para instalar con pyinstaller desde Raspberry/Linux

    pyinstaller --onedir --add-data "scan_network.sh:." --hidden-import pymongo --hidden-import pymongo.mongo_client --hidden-import pymongo.collection --hidden-import bson --hidden-import bson.codec_options --name="Net Monitor Beta" main.py

Para instalar con pyinstaller desde Windows:
    
    pyinstaller --onedir --hidden-import pymongo --hidden-import pymongo.mongo_client --hidden-import pymongo.collection --hidden-import bson --hidden-import bson.codec_options --hidden-import nmap --name="Net Monitor Beta" main.py


This project includes code generated with assistance of AI tools and manually reviewed and modified by the author.

Este proyecto incluye código generado con asistencia de herramientas de IA, manualmente revisado y modificado por el autor.

