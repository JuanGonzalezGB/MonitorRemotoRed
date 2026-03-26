"""
migrate_devices.py — migra dispositivos del config.json a MongoDB
Uso: python3 migrate_devices.py
"""
import json
import sys
import os

DEVICES = {
    "b4:e8:42:50:b3:9a": "BombilioDrums",
    "18:b9:05:db:bc:51": "BombilioStudio",
    "e0:d5:5e:ec:7c:2f": "PcSito",
    "60:83:e7:7a:c4:0c": "Router",
    "da:4f:45:c6:dc:13": "CeluChimborrio",
    "b4:e8:42:20:92:3c": "BombilioRoom",
    "b4:e8:42:24:8e:7a": "BombilioBanio",
    "b8:27:eb:a3:05:b6": "JuanitoBerry",
    "d2:e0:db:8b:e6:60": "Celu5g",
    "86:fd:77:2e:27:cb": "Amor",
}


def load_mongo_config() -> dict:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_path) as f:
        data = json.load(f)
    return data.get("mongodb", {})


def migrate():
    try:
        from pymongo import MongoClient
    except ImportError:
        print("ERROR: pymongo no instalado. Corré: pip install pymongo")
        sys.exit(1)

    mg = load_mongo_config()
    host     = mg.get("host", "192.168.0.108")
    port     = mg.get("port", 27017)
    user     = mg.get("user", "")
    password = mg.get("password", "")
    db_name  = mg.get("db", "scanner")

    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource=admin"
    else:
        uri = f"mongodb://{host}:{port}/"

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()
    except Exception as e:
        print(f"ERROR: no se pudo conectar a MongoDB: {e}")
        sys.exit(1)

    col = client[db_name]["dispositivos"]

    inserted = 0
    updated  = 0
    for mac, name in DEVICES.items():
        result = col.update_one(
            {"mac": mac},
            {"$set": {"mac": mac, "name": name}},
            upsert=True
        )
        if result.upserted_id:
            print(f"  + insertado  {mac}  →  {name}")
            inserted += 1
        else:
            print(f"  ~ actualizado {mac}  →  {name}")
            updated += 1

    print(f"\nListo: {inserted} insertados, {updated} actualizados en {db_name}.dispositivos")
    client.close()


if __name__ == "__main__":
    migrate()
