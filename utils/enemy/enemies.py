import json
from pathlib import Path


ENEMIES_PATH = Path("data/enemy_groups/elite/elite_groups.json")


def load_enemies():
    with open(
        ENEMIES_PATH,
        encoding="utf-8"
    ) as f:
        groups = json.load(f)

    enemies = {}

    for group_name, group in groups.items():
        for enemy_id, enemy_data in group.get("enemies", {}).items():
            enemy_data["category"] = "elite"
            enemies[enemy_id] = enemy_data

    return enemies


ENEMIES = load_enemies()


def get_enemy(enemy_id):
    return ENEMIES.get(enemy_id)
