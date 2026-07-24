import discord
from discord.ext import commands
from discord import app_commands
from utils.characters import get_character
from utils.character_autocomplete import character_autocomplete
from utils.icons import get_character_icon, get_talent_emoji, TALENT_SUFFIXES
from utils.talents_format import format_description

class Passives(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="passives",
        description="Shows a character's passive talents."
    )
    @app_commands.autocomplete(character=character_autocomplete)
    async def passives(
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
            title=f"{data['name']} • Passives",
            colour=discord.Colour.from_str(data["colour"])
        )

        embed.set_thumbnail(url="attachment://character.png")

        passives = data["passives"]

        for passive in passives:
            unlock = passive["unlock"].lower()

            embed.add_field(
                name=(
                    f"{get_talent_emoji(application_emojis, data['id'], unlock)} "
                    f"{passive['unlock']} • {passive['name']}"
                ),
                value=format_description(passive["description"]) + "\n\u200b",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            file=thumbnail
        )

async def setup(bot):
    await bot.add_cog(Passives(bot))