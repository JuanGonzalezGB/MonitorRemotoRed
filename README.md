#Monitor Red


Debe tener arp-scan

-----------------------------

Instalar requisitos:
     
     pip3 install -r requirements.txt

-----------------------------
En esta version se aplico patron mvc para facilitar futuros cambios.

-----------------------------

Para instalar con pyinstaller desde raspberry:

    pip3 install pymongo 
    
    pyinstaller --onedir --add-data "scan_network.sh:." --hidden-import pymongo --hidden-import pymongo.mongo_client --hidden-import pymongo.collection --hidden-import bson --hidden-import bson.codec_options main.py
