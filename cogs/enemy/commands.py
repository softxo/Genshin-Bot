import discord
from discord.ext import commands
from discord import app_commands
from utils.enemy.enemies import get_enemy
from utils.enemy.enemy_autocomplete import enemy_autocomplete
from utils.enemy.enemy_format import format_elements, format_values
from utils.enemy.shield_format import format_shields
from utils.icons import get_enemy_icon, get_enemy_splash
from utils.constants import ENEMY_ELEMENT_COLOURS, COLOURED_ELEMENT_EMOJIS, ELEMENT_NAMES, ENEMY_CATEGORY_NAMES


class Enemy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="enemy",
        description="Shows enemy information."
    )
    @app_commands.autocomplete(enemy=enemy_autocomplete)
    async def enemy(
        self,
        interaction: discord.Interaction,
        enemy: str
    ):

        data = get_enemy(enemy.lower())

        if not data:
            await interaction.response.send_message(
                "Enemy not found.",
                ephemeral=True
            )
            return

        colour = ENEMY_ELEMENT_COLOURS.get(
            data["element"][0],
            discord.Colour.light_grey()
        )

        embed = discord.Embed(
            title=f"{data["name"]} • {ENEMY_CATEGORY_NAMES[data['category']]}",
            colour=colour
        )

        icon = discord.File(
            get_enemy_icon(data, data["category"]),
            filename="enemy.webp"
        )

        splash = discord.File(
            get_enemy_splash(data, data["category"]),
            filename="splash.png"
        )

        embed.set_thumbnail(url="attachment://enemy.webp")
        embed.set_image(url="attachment://splash.png")

        if "element" in data:
            elements = ", ".join(
                f"{COLOURED_ELEMENT_EMOJIS.get(element, '')} **{ELEMENT_NAMES.get(element, element.title())}**"
                for element in data["element"]
            )

            embed.add_field(
                name="Element",
                value=elements + "\n\u200b",
                inline=False
            )

        states = list(data["res"].values())

        base = states[0]["resistance_values"]
        embed.add_field(
            name="Element",
            value=format_elements(base) + "\n\u200b",
            inline=True
        )

        embed.add_field(
            name=states[0]["display_name"] + " RES",
            value=format_values(
                states[0]["resistance_values"],
                states[0].get("immune")
            ),
            inline=True
        )

        if len(states) > 1:
            embed.add_field(
                name=states[1]["display_name"] + " RES",
                value=format_values(
                    states[1]["resistance_values"],
                    states[1].get("immune")
                ),
                inline=True
            )


        if "shield" in data:
            embed.add_field(
                name="Shield",
                value=format_shields(data["shield"]),
                inline=False
            )


        await interaction.response.send_message(
            embed=embed,
            files=[icon, splash]
        )


async def setup(bot):
    await bot.add_cog(Enemy(bot))