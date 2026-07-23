import discord
from pathlib import Path
from discord import Emoji
from typing import Optional

CHARACTER_ASSETS = Path("assets/characters")

TALENT_SUFFIXES = {
    "normal": "NA",
    "skill": "E",
    "burst": "Q",
    "a1": "A1",
    "a4": "A4",
    "utility": "Utility",
    "witch's homework": "WitchsHomework",
}

## EMOJI Helpers

def get_constellation_emoji(
        emojis,
        character_id: str,
        constellation: int
) -> Optional[Emoji]:

    name = f"{get_emoji_character_name(character_id)}_C{constellation}"

    return discord.utils.get(emojis, name=name)

def get_emoji_character_name(character_id: str) -> str:
    return "_".join(part.capitalize() for part in character_id.split("_"))

def get_talent_emoji(
        emojis,
        character_id: str,
        talent: str
) -> Optional[Emoji]:

    suffix = TALENT_SUFFIXES.get(talent)

    if suffix is None:
        return None

    return discord.utils.get(
        emojis,
        name=f"{get_emoji_character_name(character_id)}_{suffix}"
    )

def get_material_emoji(
    emojis,
    emoji_name: str
) -> str:
    emoji = discord.utils.get(
        emojis,
        name=emoji_name
    )

    return str(emoji) if emoji else ""

## ASSET Helpers

def get_constellation_icons(character_id: str) -> list[Path]:
    folder = CHARACTER_ASSETS / character_id / "constellations"

    return [
        folder / f"C{i}.webp"
        for i in range(1,7)
    ]

def get_talent_images(character_id: str) -> dict[str, Path]:
    folder = CHARACTER_ASSETS / character_id / "skills"

    return {
        "normal": folder / "Normal_Attack.webp",
        "skill": folder / "Elemental_Skill.webp",
        "burst": folder / "Elemental_Burst.webp",
        "a1": folder / "A1.webp",
        "a4" : folder / "A4.webp",
        "utility": folder / "Utility.webp",
        "witch's homework": folder / "Witch's Homework.webp",
    }

def get_character_icon(character_id: str) -> Path:
    return CHARACTER_ASSETS / character_id / "icons" / "icon.webp"

def get_character_splash(character_id: str) -> Path:
    return CHARACTER_ASSETS / character_id / "icons" / "splash.png"

def get_character_card(character_id: str) -> Path:
    return CHARACTER_ASSETS / character_id / "icons" / "card.png"