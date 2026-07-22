import discord
from discord.ext import commands
from discord import app_commands
from utils.characters import get_character
from utils.autocomplete import character_autocomplete
from utils.icons import get_character_icon
from utils.materials import GEMS

import json
from pathlib import Path

MATERIALS_PATH = Path("data/materials")


def load_json(filename):
    with open(
        MATERIALS_PATH / filename,
        encoding="utf-8"
    ) as f:
        return json.load(f)


GEMS = load_json("gems.json")
BOOKS = load_json("books.json")
COMMON = load_json("common.json")
BOSSES = load_json("boss.json")
WEEKLY = load_json("weekly.json")
LOCAL_SPECIALTIES = load_json("local_specialty.json")



class Materials(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="materials",
        description="Shows a character's Ascension and Talent materials."
    )
    @app_commands.autocomplete(character=character_autocomplete)
    async def materials(
        self,
        interaction: discord.Interaction,
        character: str
    ):
        data = get_character(character)

        if not data:
            await interaction.response.send_message(
                "Character not found.",
                ephemeral=True
            )
            return

        thumbnail = discord.File(
            get_character_icon(data["id"]),
            filename="character.png"
        )

        embed = discord.Embed(
            title=f"{data['name']} • Materials",
            colour=discord.Colour.from_str(data["colour"])
        )

        embed.set_thumbnail(url="attachment://character.png")

        materials = data["materials"]

        ascension = materials["ascension"]

        gem = GEMS[ascension["gem"]["id"]]

        embed.add_field(
            name="Character Ascension",
            value=(
                f"{gem['tiers']['sliver']} ×{ascension['gem']['sliver']}\n"
                f"{gem['tiers']['fragment']} ×{ascension['gem']['fragment']}\n"
                f"{gem['tiers']['chunk']} ×{ascension['gem']['chunk']}\n"
                f"{gem['tiers']['gemstone']} ×{ascension['gem']['gemstone']}"
            ),
            inline=False
        )

        talents = materials["talents"]

        await interaction.response.send_message(
            embed=embed,
            file=thumbnail,
        )

async def setup(bot):
    await bot.add_cog(Materials(bot))
