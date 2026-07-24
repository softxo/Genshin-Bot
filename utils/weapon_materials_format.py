import discord
from utils.materials_data import MISC
from utils.icons import get_material_emoji
from utils.materials_format import format_materials
from utils.weapon_materials import (get_weapon_material, get_common_material, get_elite_material)
from utils.constants import WEAPON_RARITY_COLOURS

def get_weapon_material_text(data, emojis):
    materials = data["materials"]

    weapon = materials["weapon_material"]
    weapon_data = get_weapon_material(weapon["id"])

    return format_materials(
        weapon_data,
        weapon,
        emojis
    )


def get_common_material_text(data, emojis):
    materials = data["materials"]

    common = materials["common"]
    common_data = get_common_material(common["id"])

    return format_materials(
        common_data,
        common,
        emojis
    )


def get_elite_material_text(data, emojis):
    materials = data["materials"]

    elite = materials["elite"]
    elite_data = get_elite_material(elite["id"])

    return format_materials(
        elite_data,
        elite,
        emojis
    )


def get_mora_text(data, emojis):
    mora = data["materials"]["mora"]

    mora_data = MISC["mora"]

    mora_emoji = get_material_emoji(
        emojis,
        mora_data["emoji"]
    )

    return (
        f"{mora_emoji} **{mora_data['name']}** ×{mora['amount']:,}"
    )

def build_weapon_materials_embed(data, emojis):
    embed = discord.Embed(
        title=f"{data['name']} • Ascension Materials",
        colour=WEAPON_RARITY_COLOURS[data["rarity"]]
    )

    embed.set_thumbnail(url="attachment://weapon.webp")

    embed.add_field(
        name="Weapon Ascension Material",
        value=get_weapon_material_text(data, emojis),
        inline=False
    )

    embed.add_field(
        name="Common Material",
        value=get_common_material_text(data, emojis),
        inline=False
    )

    embed.add_field(
        name="Elite Material",
        value=get_elite_material_text(data, emojis),
        inline=False
    )

    embed.add_field(
        name="Mora",
        value=get_mora_text(data, emojis),
        inline=False
    )

    return embed