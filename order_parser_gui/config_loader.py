import yaml
from pathlib import Path

BASE = Path(__file__).parent / "config"

def load_yaml(name: str) -> dict:
    with open(BASE / name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

UNITS = load_yaml("units.yaml")["units"]
ARRIVAL_TYPES = load_yaml("arrival_types.yaml")["arrival_types"]
DEPARTURE_TYPES = load_yaml("departure_types.yaml")["departure_types"]
