from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import yaml

_BASE = Path(__file__).parent / "config"

_cache: Dict[str, Dict[str, str]] = {}

def _load_file(fname: str, root_key: str) -> Dict[str, str]:
    path = _BASE / fname
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = yaml.safe_load(f) or {}
    node = data.get(root_key) or {}
    if not isinstance(node, dict):
        return {}
    # normalize keys/values to str
    out: Dict[str, str] = {}
    for k, v in node.items():
        if k is None:
            continue
        out[str(k)] = "" if v is None else str(v)
    return out

def reload_all() -> None:
    _cache.clear()

def get_units() -> Dict[str, str]:
    if "units" not in _cache:
        _cache["units"] = _load_file("units.yaml", "units")
    return _cache["units"]

def get_arrival_types() -> Dict[str, str]:
    if "arrival_types" not in _cache:
        _cache["arrival_types"] = _load_file("arrival_types.yaml", "arrival_types")
    return _cache["arrival_types"]

def get_departure_types() -> Dict[str, str]:
    if "departure_types" not in _cache:
        _cache["departure_types"] = _load_file("departure_types.yaml", "departure_types")
    return _cache["departure_types"]

def save_mapping(fname: str, root_key: str, mapping: Dict[str, str]) -> None:
    _BASE.mkdir(parents=True, exist_ok=True)
    path = _BASE / fname
    payload = {root_key: dict(sorted(mapping.items(), key=lambda kv: kv[0].lower()))}
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=False)
    # invalidate cache
    reload_all()
