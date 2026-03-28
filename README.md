#Monitor Red(WINDOWS)


Debe tener nmap

-----------------------------

Instalar requisitos:

     pip install python-nmap psutil

Requisitos opcionales:

     pip3 install -r requirements.txt

Esto instala pymongo, si decide no usar mongodb, el programa guardará los dispositivos en devices.json

-----------------------------
En esta version se aplico patron mvc para facilitar futuros cambios.

-----------------------------

Para instalar con pyinstaller desde raspberry:

    pip3 install pymongo 
    
    pyinstaller --onedir --hidden-import pymongo --hidden-import pymongo.mongo_client --hidden-import pymongo.collection --hidden-import bson --hidden-import bson.codec_options --hidden-import nmap main.py