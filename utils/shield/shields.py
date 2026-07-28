import json
from pathlib import Path

SHIELDS_PATH = Path("data/shields/shields.json")

with SHIELDS_PATH.open(encoding="utf-8") as f:
    SHIELDS = json.load(f)


def get_shield(shield_id: str):
    return SHIELDS.get(shield_id)