import discord
from discord.ext import commands
from discord import app_commands
from utils.weapons import get_weapon
from utils.weapon_autocomplete import weapon_autocomplete
from utils.weapon_materials_format import build_weapon_materials_embed
from utils.icons import get_weapon_icon

class Weapons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="weaponmaterials",
        description="Shows a weapon's ascension materials."
    )
    @app_commands.autocomplete(
        weapon=weapon_autocomplete
    )
    async def weaponmaterials(
        self,
        interaction: discord.Interaction,
        weapon: str
    ):
        data = get_weapon(weapon)

        if data is None:
            await interaction.response.send_message(
                "Weapon not found.",
                ephemeral=True
            )
            return

        if "materials" not in data:
            await interaction.response.send_message(
                "This weapon has no ascension materials.",
                ephemeral=True
            )
            return

        embed = build_weapon_materials_embed(
            data,
            self.bot.application_emojis
        )

        icon_path = get_weapon_icon(data)

        if icon_path.exists():
            file = discord.File(
                icon_path,
                filename="weapon.webp"
            )

            await interaction.response.send_message(
                embed=embed,
                file=file
            )
        else:
            await interaction.response.send_message(
                embed=embed
            )

async def setup(bot):
    await bot.add_cog(Weapons(bot))