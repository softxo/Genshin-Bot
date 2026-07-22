import discord
from discord.ext import commands
from discord import app_commands
from utils.icons import get_character_icon, get_constellation_emoji
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

        application_emojis = await self.bot.fetch_application_emojis()

        thumbnail = discord.File(
            get_character_icon(data["id"]),
            filename="character.png"
        )

        embed = discord.Embed(
            title=f"{data['name']} • Constellations",
            colour=discord.Colour.from_str(data["colour"])
        )

        embed.set_thumbnail(url="attachment://character.png")

        for i, constellation in enumerate(data["constellations"], start=1):
            emoji = get_constellation_emoji(
                application_emojis,
                data["id"],
                i
            )

            emoji_text = str(emoji) if emoji else "⭐"

            description = constellation["description"]

            if isinstance(description, list):
                description = "\n".join(description)

            embed.add_field(
                name=f"{emoji_text} C{i} • **{constellation['name']}**",
                value=description + "\n\u200b",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            file=thumbnail
        )

async def setup(bot):
    await bot.add_cog(Constellations(bot))
