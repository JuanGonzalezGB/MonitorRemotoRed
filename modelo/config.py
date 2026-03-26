"""
model/config.py — config local en JSON + dispositivos en MongoDB
- Con Mongo disponible: dispositivos solo en Mongo
- Con Mongo caído: fallback a JSON, resincroniza cuando Mongo vuelve
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
        self._mongo_client = None
        self._collection = None
        self._fallback_devices: dict = {}  # cache JSON cuando Mongo está caído
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
            # Guardar devices del JSON como fallback inicial
            self._fallback_devices = self._data.pop("devices", {})
        except json.JSONDecodeError as e:
            print(f"[config] Error en config.json: {e}")
            self._data = dict(DEFAULT)

    def _save_json(self):
        try:
            with open(self.path, "w") as f:
                # Nunca escribir devices en el JSON
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

            self._mongo_client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            self._mongo_client.server_info()
            self._collection = self._mongo_client[db_name]["dispositivos"]
            print(f"[config] MongoDB conectado: {host}:{port}/{db_name}")

            # Si había dispositivos en el JSON como fallback, migrarlos
            self._sync_fallback_to_mongo()

        except ImportError:
            print("[config] pymongo no instalado — usando JSON como fallback")
        except Exception as e:
            print(f"[config] MongoDB no disponible ({e}) — usando JSON como fallback")
            self._collection = None

    def _sync_fallback_to_mongo(self):
        """Si había devices en el JSON, los sube a Mongo sin pisar los existentes."""
        if not self._fallback_devices or not self._mongo_ok:
            return
        for mac, info in self._fallback_devices.items():
            name = info.get("name")
            if not name:
                continue
            existing = self._collection.find_one({"mac": mac})
            if not existing:
                self._collection.insert_one({"mac": mac, "name": name})
                print(f"[config] Migrado de JSON a Mongo: {mac} → {name}")
        self._fallback_devices = {}

    def _try_reconnect(self):
        """Intenta reconectar a Mongo si está caído."""
        if not self._mongo_ok:
            self._connect_mongo()

    @property
    def _mongo_ok(self) -> bool:
        return self._collection is not None

    # ── Dispositivos ──────────────────────────────────────────────────────────

    @property
    def devices(self) -> dict:
        self._try_reconnect()
        if self._mongo_ok:
            try:
                return {
                    d["mac"]: {"name": d["name"]}
                    for d in self._collection.find({}, {"_id": 0, "mac": 1, "name": 1})
                }
            except Exception as e:
                print(f"[config] Error leyendo Mongo: {e}")
                self._collection = None
        return self._fallback_devices

    def device_name(self, mac: str) -> str | None:
        self._try_reconnect()
        if self._mongo_ok:
            try:
                doc = self._collection.find_one({"mac": mac}, {"_id": 0, "name": 1})
                return doc["name"] if doc else None
            except Exception as e:
                print(f"[config] Error leyendo dispositivo: {e}")
                self._collection = None
        return self._fallback_devices.get(mac, {}).get("name")

    def set_device_name(self, mac: str, name: str):
        self._try_reconnect()

        # Siempre actualizar fallback local
        self._fallback_devices.setdefault(mac, {})["name"] = name

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
                print(f"[config] Error guardando en Mongo: {e} — guardado solo en memoria")
                self._collection = None

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

    @property
    def ping_warn_ms(self) -> int:
        return self._data.get("ping_warn_ms", DEFAULT["ping_warn_ms"])
