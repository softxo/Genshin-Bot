import discord
from discord.ext import commands
from discord import app_commands
from utils.characters import get_character
from utils.autocomplete import character_autocomplete
from utils.constants import ELEMENT_EMOJIS, WEAPON_EMOJIS

class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="character",
        description="Shows character information."
    )
    @app_commands.autocomplete(character=character_autocomplete)
    async def character(
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

        icon = discord.File(
            f"assets/characters/{data['id']}/{data['images']['icon']}",
            filename="icon.webp"
        )

        splash = discord.File(
            f"assets/characters/{data['id']}/{data['images']['splash']}",
            filename="splash.png"
        )

        embed = discord.Embed(
            title=data["name"],
            description=data["description"],
            colour=discord.Colour.from_str(data["colour"])
        )

        embed.set_thumbnail(
            url="attachment://icon.webp"
        )

        embed.add_field(
            name="Title",
            value=data["title"]
        )

        embed.add_field(
            name="Affiliation",
            value=data["affiliation"]
        )

        embed.add_field(
            name="Constellation",
            value=data["constellation"]
        )

        embed.add_field(
            name="Rarity",
            value="★" * data["rarity"]
        )

        embed.add_field(
            name="Element",
            value=f"{ELEMENT_EMOJIS[data['element']]} {data['element'].title()}"
        )

        embed.add_field(
            name="Weapon",
            value=f"{WEAPON_EMOJIS[data['weapon']]} {data['weapon'].title()}"
        )

        embed.add_field(
            name="Version",
            value=data["version"]
        )

        embed.add_field(
            name="Release",
            value=data["release"]
        )

        embed.add_field(
            name="Birthday",
            value=data["birthday"]
        )

        embed.set_image(
            url="attachment://splash.png"
        )

        await interaction.response.send_message(
            embed=embed,
            files=[icon, splash]
        )

async def setup(bot):
    await bot.add_cog(Character(bot))