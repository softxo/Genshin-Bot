from pathlib import Path
import json

CHARACTERS = {}

CONSTELLATION_ICONS = {
    "amber": {
        1: "<:Amber_C1:1529117367194357780>",
        2: "<:Amber_C2:1529117368511627344>",
        3: "<:Amber_C3:1529117370017382481>",
        4: "<:Amber_C4:1529117371556561016>",
        5: "<:Amber_C5:1529117373066379264>",
        6: "<:Amber_C6:1529117374349836298>"
    },
    "barbara": {
        1: "<:Barbara_C1:1529178807209168896>",
        2: "<:Barbara_C2:1529178809449054351>",
        3: "<:Barbara_C3:1529178811181170758>",
        4: "<:Barbara_C4:1529178812745515008>",
        5: "<:Barbara_C5:1529178814192685076>",
        6: "<:Barbara_C6:1529178815501176842>"
    },
    "beidou": {
        1: "<:Beidou_C1:1529179325050388571>",
        2: "<:Beidou_C2:1529179327793467534>",
        3: "<:Beidou_C3:1529179329748009153>",
        4: "<:Beidou_C4:1529179331119812648>",
        5: "<:Beidou_C5:1529179332361326731>",
        6: "<:Beidou_C6:1529179333841649676>"
    },
    "": {
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: ""
    },
    "": {
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: ""
    },
    "": {
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: ""
    },
    "": {
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: ""
    }
}

def load_characters():
    CHARACTERS.clear()

    for file in Path("data/characters").glob("*.json"):
        print(f"Loading {file}")

        with open(file, encoding="utf-8") as f:
            character = json.load(f)

        CHARACTERS[character["id"]] = character