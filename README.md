#Monitor Red(WINDOWS)

Debe tener nmap

-----------------------------

#Instalar requisitos:

descargue nmap: https://nmap.org/ o:

     winget install nmap

luego:

     pip3 install -r requirements.txt

-----------------------------

Para instalar con pyinstaller desde windows:
    
    pyinstaller --onedir --hidden-import pymongo --hidden-import pymongo.mongo_client --hidden-import pymongo.collection --hidden-import bson --hidden-import bson.codec_options --hidden-import nmap --name="Net Monitor Beta" main.py
