import json
from pathlib import Path

WEAPONS_PATH = Path("data/weapons")

WEAPONS = {}


def load_weapons():
    """Loads every weapon from every weapon JSON file"""

    WEAPONS.clear()

    if not WEAPONS_PATH.exists():
        print(f"Weapon folder not found: {WEAPONS_PATH}")
        return

    for json_file in WEAPONS_PATH.rglob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            weapon = json.load(f)

        WEAPONS[weapon["id"]] = weapon

    print(f"Loaded {len(WEAPONS)} weapon(s).")


def get_weapon(weapon_id: str):
    """Return a weapon by its ID."""
    return WEAPONS.get(weapon_id)


def get_all_weapons():
    """Return every loaded weapon."""
    return WEAPONS