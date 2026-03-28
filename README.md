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

Para instalar con pyinstaller desde Raspberry/Linux

    pyinstaller --onedir --add-data "scan_network.sh:." --hidden-import pymongo --hidden-import pymongo.mongo_client --hidden-import pymongo.collection --hidden-import bson --hidden-import bson.codec_options --name="Net Monitor Beta" main.py

Para instalar con pyinstaller desde Windows:
    
    pyinstaller --onedir --hidden-import pymongo --hidden-import pymongo.mongo_client --hidden-import pymongo.collection --hidden-import bson --hidden-import bson.codec_options --hidden-import nmap --name="Net Monitor Beta" main.py


