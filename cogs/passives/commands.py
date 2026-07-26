import discord
from discord.ext import commands
from discord import app_commands
from utils.character.characters import get_character
from utils.character.character_autocomplete import character_autocomplete
from utils.icons import get_character_icon, get_talent_emoji
from utils.talents_format import format_description

class Passives(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _send_passives(self, destination, character: str):
        character = character.lower().replace(" ", "_")

        data = get_character(character)

        if data is None:
            await destination.send("Character not found.")
            return

        thumbnail = discord.File(
            get_character_icon(data["id"]),
            filename="character.png"
        )

        emojis = self.bot.application_emojis

        embed = discord.Embed(
            title=f"{data['name']} • Passives",
            colour=discord.Colour.from_str(data["colour"])
        )

        embed.set_thumbnail(url="attachment://character.png")

        for passive in data["passives"]:
            unlock = passive["unlock"].lower()

            embed.add_field(
                name=(
                    f"{get_talent_emoji(emojis, data['id'], unlock)} "
                    f"{passive['unlock']} • {passive['name']}"
                ),
                value=format_description(passive["description"]) + "\n\u200b",
                inline=False
            )

        await destination.send(
            embed=embed,
            file=thumbnail
        )

    @app_commands.command(
        name="passives",
        description="Shows a character's passive talents."
    )
    @app_commands.autocomplete(character=character_autocomplete)
    async def passives_slash(
        self,
        interaction: discord.Interaction,
        character: str
    ):
        await interaction.response.defer()

        await self._send_passives(
            interaction.followup,
            character
        )

    @commands.command(
        name="passives",
        aliases=["passive"]
    )
    async def passives(
        self,
        ctx: commands.Context,
        *,
        character: str
    ):
        await self._send_passives(
            ctx,
            character
        )

async def setup(bot):
    await bot.add_cog(Passives(bot))