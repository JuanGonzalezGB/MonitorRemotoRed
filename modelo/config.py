"""
model/config.py — config local en JSON + dispositivos en MongoDB
- Con Mongo disponible: dispositivos en MongoDB
- Con Mongo caído: dispositivos en devices.json
- Cuando Mongo vuelve: migra devices.json a Mongo automáticamente
"""
import json
import os
import sys

DEFAULT = {
    "subnet": "192.168.0.0/24",
    "scan_interval": 2,
    "ping_warn_ms": 20,
    "mongodb": {
        "host": "localhost",
        "port": 27017,
        "user": "",
        "password": "",
        "db": "scanner"
    }
}


def _base_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    def __init__(self):
        self.path         = os.path.join(_base_path(), "config.json")
        self._devices_path = os.path.join(_base_path(), "devices.json")
        self._data: dict  = {}
        self._collection  = None
        self._use_json    = False
        self._load()
        self._connect_mongo()

    # ── config.json ───────────────────────────────────────────────────────────

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
            print(f"[config] Error guardando config.json: {e}")

    # ── devices.json ──────────────────────────────────────────────────────────

    def _load_devices_json(self) -> dict:
        if not os.path.exists(self._devices_path):
            return {}
        try:
            with open(self._devices_path) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_devices_json(self, devices: dict):
        try:
            with open(self._devices_path, "w") as f:
                json.dump(devices, f, indent=4)
        except Exception as e:
            print(f"[config] Error guardando devices.json: {e}")

    # ── MongoDB ───────────────────────────────────────────────────────────────

    def _connect_mongo(self):
        try:
            from pymongo import MongoClient
            mg       = self._data.get("mongodb", {})
            host     = mg.get("host", "localhost")
            port     = mg.get("port", 27017)
            user     = mg.get("user", "")
            password = mg.get("password", "")
            db_name  = mg.get("db", "scanner")

            uri = (
                f"mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource=admin"
                if user and password else
                f"mongodb://{host}:{port}/"
            )

            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            client.server_info()
            self._collection = client[db_name]["dispositivos"]
            self._use_json = False
            print(f"[config] MongoDB conectado: {host}:{port}/{db_name}")
            self._migrate_json_to_mongo()
        except ImportError:
            print("[config] pymongo no instalado — usando devices.json")
            self._use_json = True
        except Exception as e:
            print(f"[config] MongoDB no disponible ({e}) — usando devices.json")
            self._use_json = True
            self._collection = None

    def _migrate_json_to_mongo(self):
        """Sube devices.json a Mongo si existe, sin pisar los existentes."""
        local = self._load_devices_json()
        if not local:
            return
        for mac, info in local.items():
            name = info.get("name")
            if name and not self._collection.find_one({"mac": mac}):
                self._collection.insert_one({"mac": mac, "name": name})
                print(f"[config] Migrado a Mongo: {mac} → {name}")
        os.remove(self._devices_path)
        print("[config] devices.json migrado y eliminado")

    @property
    def _mongo_ok(self) -> bool:
        return self._collection is not None and not self._use_json

    # ── Dispositivos ──────────────────────────────────────────────────────────

    @property
    def devices(self) -> dict:
        if self._mongo_ok:
            try:
                return {
                    d["mac"]: {"name": d["name"]}
                    for d in self._collection.find({}, {"_id": 0, "mac": 1, "name": 1})
                }
            except Exception as e:
                print(f"[config] Error leyendo Mongo: {e}")
                self._collection = None
                self._use_json = True
        return self._load_devices_json()

    def device_name(self, mac: str) -> str | None:
        if self._mongo_ok:
            try:
                doc = self._collection.find_one({"mac": mac}, {"_id": 0, "name": 1})
                return doc["name"] if doc else None
            except Exception as e:
                print(f"[config] Error leyendo dispositivo: {e}")
                self._collection = None
                self._use_json = True
        return self._load_devices_json().get(mac, {}).get("name")

    def set_device_name(self, mac: str, name: str):
        if self._mongo_ok:
            try:
                self._collection.update_one(
                    {"mac": mac},
                    {"$set": {"mac": mac, "name": name}},
                    upsert=True
                )
                print(f"[config] Guardado en Mongo: {mac} → {name}")
                return
            except Exception as e:
                print(f"[config] Error guardando en Mongo: {e}")
                self._collection = None
                self._use_json = True

        # Fallback devices.json
        devices = self._load_devices_json()
        devices.setdefault(mac, {})["name"] = name
        self._save_devices_json(devices)
        print(f"[config] Guardado en devices.json: {mac} → {name}")

    def register_device(self, mac: str):
        """Registra un dispositivo nuevo con su MAC como nombre si no existe."""
        if self._mongo_ok:
            try:
                self._collection.update_one(
                    {"mac": mac},
                    {"$setOnInsert": {"mac": mac, "name": mac}},
                    upsert=True
                )
            except Exception as e:
                print(f"[config] Error registrando en Mongo: {e}")
                return
        else:
            devices = self._load_devices_json()
            if mac not in devices:
                devices[mac] = {"name": mac}
                self._save_devices_json(devices)

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
    def mongo(self) -> dict:
        return self._data.get("mongodb", DEFAULT["mongodb"])

    @mongo.setter
    def mongo(self, value: dict):
        self._data["mongodb"] = value
        self._save_json()
        # Reconectar con las nuevas credenciales
        self._collection = None
        self._use_json = False
        self._connect_mongo()

    @property
    def ping_warn_ms(self) -> int:
        return self._data.get("ping_warn_ms", DEFAULT["ping_warn_ms"])
