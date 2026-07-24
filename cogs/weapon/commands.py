import discord
from discord.ext import commands
from discord import app_commands
from utils.weapons import get_weapon
from utils.weapon_autocomplete import weapon_autocomplete
from utils.weapon_materials import get_weapon_material
from utils.constants import WEAPON_RARITY_COLOURS, STAT_NAMES, PERCENT_STATS
from utils.icons import get_weapon_icon_path, get_material_emoji


class Weapon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="weapon",
        description="Shows information about a weapon."
    )
    @app_commands.autocomplete(
        weapon=weapon_autocomplete
    )
    async def weapon(
        self,
        interaction: discord.Interaction,
        weapon: str,
        refinement: app_commands.Range[int, 1, 5] = 1
    ):
        data = get_weapon(weapon)

        if data is None:
            await interaction.response.send_message(
                "Weapon not found.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=data["name"],
            description=data["description"],
            colour=WEAPON_RARITY_COLOURS[data["rarity"]]
        )

        embed.add_field(
            name="Weapon Type",
            value=data["weapon_type"].replace("_", " ").title() + "\n\u200b",
            inline=True
        )

        embed.add_field(
            name="Rarity",
            value="★" * data["rarity"],
            inline=True
        )

        embed.add_field(
            name="Max Level",
            value=str(data["max_level"]) + "\n\u200b",
            inline=True
        )

        embed.add_field(
            name=STAT_NAMES[data["main_stat"]["type"]],
            value=str(data["main_stat"]["value"]),
            inline=True
        )

        secondary = data["secondary_stat"]

        if secondary is None:
            secondary_text = "None"
        else:
            value = secondary["value"]

            if secondary["type"] in PERCENT_STATS:
                value = f"{value}%"

            secondary_text = (
                f'{STAT_NAMES[secondary["type"]]} +{value}'
            )

        embed.add_field(
            name="Secondary Stat",
            value=secondary_text,
            inline=False
        )

        if data["passive"] is None:
            passive_text = "None"
        else:
            passive = data["passive"]
            passive_text = (
                f'**{passive["name"]}**\n'
                f'{passive["description"][f"r{refinement}"]}'
            )

        embed.add_field(
            name="Passive",
            value=passive_text + "\n\u200b",
            inline=False
        )

        materials = data.get("materials", {})

        weapon_material = materials.get("weapon_material")

        if weapon_material:
            material_data = get_weapon_material(
                weapon_material["id"]
            )

            if material_data:
                text = ""

                for tier, amount in weapon_material.items():
                    if tier.startswith("tier"):
                        material = material_data["tiers"][tier]

                        emoji = get_material_emoji(
                            self.bot.emojis,
                            material["emoji"]
                        )

                        text += (
                                f"{emoji} {material['name']} ×{amount}\n"
                        )

                embed.add_field(
                    name="Weapon Ascension Materials",
                    value=text,
                    inline=False
                )

        embed.set_footer(
            text=f"Refinement Rank {refinement} • Level {data['max_level']}"
        )

        icon_path = get_weapon_icon_path(data)
        print(icon_path)
        print(icon_path.exists())

        if icon_path.exists():
            file = discord.File(icon_path, filename="weapon.webp")
            embed.set_thumbnail(url="attachment://weapon.webp")

            await interaction.response.send_message(
                embed=embed,
                file=file
            )
        else:
            await interaction.response.send_message(
                embed=embed
            )


async def setup(bot):
    await bot.add_cog(Weapon(bot))