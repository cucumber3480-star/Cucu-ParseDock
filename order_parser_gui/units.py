# Нормалізація підрозділів через YAML-конфіг
from config_store import get_units

def normalize_unit(code: str) -> str:
    if not code:
        return ""
    return get_units().get(code, code)
