import json
from pathlib import Path

MATERIALS_PATH = Path("data/materials")

with open(MATERIALS_PATH / "miscellaneous.json", encoding="utf-8") as f:
    MISC = json.load(f)