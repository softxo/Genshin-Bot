import json
from pathlib import Path

PATH = Path("data/materials/weapon_materials.json")

with open(PATH, "r", encoding="utf-8") as f:
    WEAPON_MATERIALS = json.load(f)


def get_weapon_material(material_id):
    return WEAPON_MATERIALS.get(material_id)