"""
controlador/repository.py
Lee scanner.scans (escrito exclusivamente por el servicio collector).
No escribe nada — dueño de scans es el collector.
"""
from datetime import datetime
from modelo.device import Device
from pymongo import MongoClient

_STALE_SECONDS = 300  # 5 min sin aparecer = offline


def _get_scans_col(mongo_cfg: dict):
    user     = mongo_cfg.get("user", "")
    password = mongo_cfg.get("password", "")
    host     = mongo_cfg.get("host", "localhost")
    port     = mongo_cfg.get("port", 27017)
    db_name  = mongo_cfg.get("db", "scanner")
    uri = (
        f"mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource=admin"
        if user and password else
        f"mongodb://{host}:{port}/"
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    return client[db_name]["scans"]


def get_devices(mongo_cfg: dict) -> list[Device]:
    """Lee scanner.scans y devuelve la lista de Device con estado online/offline."""
    try:
        col = _get_scans_col(mongo_cfg)
        now = datetime.utcnow()
        devices = []
        for doc in col.find({}, {"_id": 0}):
            mac = doc.get("mac", "").lower()
            if not mac:
                continue
            last_seen = doc.get("last_seen")
            online = bool(
                last_seen and (now - last_seen).total_seconds() < _STALE_SECONDS
            )
            devices.append(Device(
                ip=doc.get("ip", ""),
                mac=mac,
                vendor=doc.get("vendor", ""),
                ping_ms=doc.get("ping_ms") if online else None,
                online=online,
            ))
        return devices
    except Exception as e:
        print(f"[repository] Error leyendo scanner.scans: {e}")
        return []


def get_last_scan_time(mongo_cfg: dict) -> str | None:
    try:
        col = _get_scans_col(mongo_cfg)
        doc = col.find_one({}, {"last_seen": 1}, sort=[("last_seen", -1)])
        if doc and doc.get("last_seen"):
            return doc["last_seen"].strftime("%H:%M:%S")
    except Exception:
        pass
    return None