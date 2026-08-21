import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

ACHIEVEMENTS_FILE = (
    BASE_DIR
    / "data"
    / "achievements"
    / "achievements.json"
)


def load_achievements() -> list[dict]:
    with open(
        ACHIEVEMENTS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return data.get("achievements", [])