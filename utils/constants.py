import discord

ELEMENT_EMOJIS = {
    "pyro": "<:Pyro:1529166535070056518>",
    "hydro": "<:Hydro:1529166533086150888>",
    "electro": "<:Electro:1529166530645069995>",
    "cryo": "<:Cryo:1529166526140387452>",
    "dendro": "<:Dendro:1529166528749113534>",
    "geo": "<:Geo:1529166532096037016>",
    "anemo": "<:Anemo:1529166524907258007>",
}

ELEMENT_NAMES = {
    "physical": "Physical",
    "pyro": "Pyro",
    "hydro": "Hydro",
    "electro": "Electro",
    "cryo": "Cryo",
    "dendro": "Dendro",
    "anemo": "Anemo",
    "geo": "Geo",
}

ENEMY_CATEGORY_NAMES = {
    "common": "Common Enemy",
    "elite": "Elite Enemy",
    "boss": "Normal Boss",
    "weekly": "Weekly Boss",
}

ENEMY_ELEMENT_COLOURS = {
    "physical": discord.Colour.light_grey(),
    "pyro": discord.Colour.orange(),
    "hydro": discord.Colour.blue(),
    "electro": discord.Colour.purple(),
    "cryo": discord.Colour.from_rgb(130, 220, 255),
    "dendro": discord.Colour.green(),
    "anemo": discord.Colour.teal(),
    "geo": discord.Colour.gold(),
}

SHIELD_EMOJIS = {
    "elementless": "<:Shield:1530937059722924213>",
    "void": "<:Shield_Void:1530937062646349834>",
    "deepdark": "<:Shield_Deepdark:1530937061350047834>",

    "nightsoul_aligned_attacks": "",
    "lunar_charged": "<:Lunar_Charged:1531803193649135786>",
    "lunar_bloom": "<:Lunar_Bloom:1531803140909699132>",
    "lunar_crystallize": "<:Lunar_Crystallize:1531803056222765208>",
    "burning_reaction": "<:Burning_Reaction:1531803227417477262>"
}

SHIELD_COLOURS = {
    "pyro": discord.Colour.orange(),
    "hydro": discord.Colour.blue(),
    "electro": discord.Colour.purple(),
    "cryo": discord.Colour.from_rgb(130, 220, 255),
    "dendro": discord.Colour.green(),
    "anemo": discord.Colour.teal(),
    "geo": discord.Colour.gold(),
    "elementless": 0xFFFFFF,
    "void": 0x5A2DA6,
    "deepdark": 0x2B0F3F
}

WEAPON_EMOJIS = {
    "bow": "<:Bow:1529165007445561454>",
    "sword": "<:Sword:1529164852529205350>",
    "claymore": "<:Claymore:1529164849727410217>",
    "polearm": "<:Polearm:1529164851157667851>",
    "catalyst": "<:Catalyst:1529164848397816021>"
}

COLOURED_ELEMENT_EMOJIS = {
    "pyro": "<:Element_Pyro:1530806714675232768>",
    "hydro": "<:Element_Hydro:1530806713244975246>",
    "electro": "<:Element_Electro:1530806709952450630>",
    "cryo": "<:Element_Cryo:1530806706504732703>",
    "dendro": "<:Element_Dendro:1530806708266598490>",
    "geo": "<:Element_Geo:1530806711617585232>",
    "anemo": "<:Element_Anemo:1530806704814559243>",
    "physical": "<:Element_Physical:1530823447041540156>"
}

ASCENSION_GEM_COSTS = {
    "sliver":    [1, 0, 0, 0, 0, 0],
    "fragment":  [0, 3, 2, 0, 4, 0],
    "chunk":     [0, 0, 0, 3, 2, 0],
    "gemstone":  [0, 0, 0, 0, 0, 6],
}

ASCENSION_BOSS_COSTS = [0, 2, 4, 8, 12, 20]

ASCENSION_LOCAL_COSTS = [3, 10, 20, 30, 45, 60]

ASCENSION_COMMON_COSTS = {
    "tier1": [3, 0, 0, 0, 0, 15],
    "tier2": [0, 12, 8, 0, 18, 0],
    "tier3": [0, 0, 0, 12, 0, 24],
}

TALENT_BOOK_COSTS = {
    "teachings":    [3, 2, 4, 6, 9, 0, 0, 0, 0],
    "guide":        [0, 0, 0, 0, 0, 4, 6, 12, 4],
    "philosophies": [0, 0, 0, 0, 0, 0, 0, 0, 16],
}

TALENT_COMMON_COSTS = {
    "tier1": [6, 3, 4, 6, 9, 0, 0, 0, 0],
    "tier2": [0, 0, 0, 0, 0, 4, 6, 9, 0],
    "tier3": [0, 0, 0, 0, 0, 0, 0, 0, 12],
}

TALENT_WEEKLY_COSTS = [0, 0, 0, 0, 0, 1, 1, 2, 2]

TALENT_CROWN_COSTS = [0, 0, 0, 0, 0, 0, 0, 0, 1]

TALENT_MORA_COSTS = [
    12500,   # 1 → 2
    17500,   # 2 → 3
    25000,   # 3 → 4
    30000,   # 4 → 5
    37500,   # 5 → 6
    120000,  # 6 → 7
    260000,  # 7 → 8
    450000,  # 8 → 9
    700000   # 9 → 10
]

ASCENSION_MORA_COSTS = [
    20000,   # 20 → 40
    40000,   # 40 → 50
    60000,   # 50 → 60
    80000,   # 60 → 70
    100000,  # 70 → 80
    120000   # 80 → 90
]

LEVEL_MORA_COSTS = [
    24200,   # 1  → 20
    115800,  # 20 → 40
    116000,  # 40 → 50
    171000,  # 50 → 60
    239200,  # 60 → 70
    322400,  # 70 → 80
    684800   # 80 → 9
]

ASCENSION_EXP_COSTS = {
    "wanderers_advice": 12,
    "adventurers_experience": 11,
    "heros_wit": 415
}

ASCENSION_PHASES = [
    "20 → 40",
    "40 → 50",
    "50 → 60",
    "60 → 70",
    "70 → 80",
    "80 → 90",
]

TALENT_LEVELS = [
    "1 → 2",
    "2 → 3",
    "3 → 4",
    "4 → 5",
    "5 → 6",
    "6 → 7",
    "7 → 8",
    "8 → 9",
    "9 → 10",
]

WEAPON_RARITY_COLOURS = {
    1: 0x8E8E8E,
    2: 0x4CAF50,
    3: 0x3F51B5,
    4: 0x9C27B0,
    5: 0xF4B400,
}

STAT_NAMES = {
    "base_atk": "Base ATK",
    "hp_percent": "HP",
    "atk_percent": "ATK",
    "def_percent": "DEF",
    "elemental_mastery": "Elemental Mastery",
    "energy_recharge": "Energy Recharge",
    "crit_rate": "CRIT Rate",
    "crit_dmg": "CRIT DMG",
    "physical_dmg_bonus": "Physical DMG Bonus",
}

REFERENCE_NAMES = {
    "max_hp": "Max HP",
    "base_hp": "Base HP",
    "max_atk": "Max ATK",
    "base_atk": "Base ATK",
    "max_def": "Max DEF",
    "base_def": "Base DEF",
}

STAT_EMOJIS = {
    "hp" : "<:HP:1530927836993552576>"
}

PERCENT_STATS = {
    "hp_percent",
    "atk_percent",
    "def_percent",
    "crit_rate",
    "crit_dmg",
    "energy_recharge",
    "healing_bonus",
    "physical_dmg_bonus",
    "pyro_dmg_bonus",
    "hydro_dmg_bonus",
    "cryo_dmg_bonus",
    "electro_dmg_bonus",
    "anemo_dmg_bonus",
    "geo_dmg_bonus",
    "dendro_dmg_bonus",
}

### Colour Codes:
# Pyro: #ef7a35
# Hydro: #54b7f0
# Electro: #b08fc2
# Cryo: #a0d7e4
# Dendro: #a6c938
# Geo: ccb133
# Anemo: #75c2aa