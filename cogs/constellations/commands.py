import discord
from discord.ext import commands
from discord import app_commands
from utils.data import CONSTELLATION_ICONS
from utils.characters import get_character
from utils.autocomplete import character_autocomplete

class Constellations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="constellations",
        description="Shows a character's constellations."
    )
    @app_commands.autocomplete(character=character_autocomplete)
    async def constellations(
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

        image = discord.File(
            f"assets/characters/{data['id']}/{data['images']['icon']}",
            filename="character.png"
        )

        embed = discord.Embed(
            title=f"{data['name']} | Constellations",
            colour=discord.Colour.from_str(data["colour"])
        )

        embed.set_thumbnail(url="attachment://character.png")

        for i, constellation in enumerate(data["constellations"], start=1):
            icon = CONSTELLATION_ICONS[data["id"]][i]

            description = constellation["description"]

            if isinstance(description, list):
                description = "\n".join(description)

            embed.add_field(
                name=f"{icon} C{i} • **{constellation['name']}**",
                value=description,
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            file=image
        )

async def setup(bot):
    await bot.add_cog(Constellations(bot))
