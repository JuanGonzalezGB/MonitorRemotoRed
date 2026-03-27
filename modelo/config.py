"""
model/config.py — config local en JSON + dispositivos en MongoDB
- Dispositivos: solo en MongoDB
- Subnet, scan_interval, ping_warn_ms: en config.json local
"""
import json
import os
import sys

DEFAULT = {
    "subnet": "192.168.0.0/24",
    "scan_interval": 2,
    "ping_warn_ms": 20,
    "mongodb": {
        "host": "192.168.0.108",
        "port": 27017,
        "user": "",
        "password": "",
        "db": "scanner"
    }
}


def _config_path() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config.json")


class Config:
    def __init__(self):
        self.path = _config_path()
        self._data: dict = {}
        self._collection = None
        self._load()
        self._connect_mongo()

    # ── JSON ──────────────────────────────────────────────────────────────────

    def _load(self):
        if not os.path.exists(self.path):
            self._data = dict(DEFAULT)
            self._save_json()
            return
        try:
            with open(self.path) as f:
                self._data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[config] Error en config.json: {e}")
            self._data = dict(DEFAULT)

    def _save_json(self):
        try:
            with open(self.path, "w") as f:
                data = {k: v for k, v in self._data.items() if k != "devices"}
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[config] Error guardando JSON: {e}")

    # ── MongoDB ───────────────────────────────────────────────────────────────

    def _connect_mongo(self):
        try:
            from pymongo import MongoClient
            mg = self._data.get("mongodb", {})
            host     = mg.get("host", "localhost")
            port     = mg.get("port", 27017)
            user     = mg.get("user", "")
            password = mg.get("password", "")
            db_name  = mg.get("db", "scanner")

            if user and password:
                uri = f"mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource=admin"
            else:
                uri = f"mongodb://{host}:{port}/"

            from pymongo import MongoClient
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            client.server_info()
            self._collection = client[db_name]["dispositivos"]
            print(f"[config] MongoDB conectado: {host}:{port}/{db_name}")
        except ImportError:
            print("[config] pymongo no instalado")
        except Exception as e:
            print(f"[config] MongoDB no disponible: {e}")

    @property
    def _mongo_ok(self) -> bool:
        return self._collection is not None

    # ── Dispositivos ──────────────────────────────────────────────────────────

    @property
    def devices(self) -> dict:
        if not self._mongo_ok:
            return {}
        try:
            return {
                d["mac"]: {"name": d["name"]}
                for d in self._collection.find({}, {"_id": 0, "mac": 1, "name": 1})
            }
        except Exception as e:
            print(f"[config] Error leyendo devices: {e}")
            return {}

    def device_name(self, mac: str) -> str | None:
        if not self._mongo_ok:
            return None
        try:
            doc = self._collection.find_one({"mac": mac}, {"_id": 0, "name": 1})
            return doc["name"] if doc else None
        except Exception as e:
            print(f"[config] Error leyendo dispositivo: {e}")
            return None

    def set_device_name(self, mac: str, name: str):
        if not self._mongo_ok:
            print("[config] MongoDB no disponible, nombre no guardado")
            return
        try:
            self._collection.update_one(
                {"mac": mac},
                {"$set": {"mac": mac, "name": name}},
                upsert=True
            )
            print(f"[config] Guardado en Mongo: {mac} → {name}")
        except Exception as e:
            print(f"[config] Error guardando dispositivo: {e}")

    # ── Propiedades locales ───────────────────────────────────────────────────

    @property
    def subnet(self) -> str:
        return self._data.get("subnet", DEFAULT["subnet"])

    @subnet.setter
    def subnet(self, value: str):
        if "/" not in value:
            value += "/24"
        self._data["subnet"] = value
        self._save_json()

    @property
    def scan_interval(self) -> int:
        return self._data.get("scan_interval", DEFAULT["scan_interval"])

    @scan_interval.setter
    def scan_interval(self, value: int):
        self._data["scan_interval"] = max(1, value)
        self._save_json()

    @property
    def ping_warn_ms(self) -> int:
        return self._data.get("ping_warn_ms", DEFAULT["ping_warn_ms"])
