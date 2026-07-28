import discord
from discord.ext import commands
from discord import app_commands
from utils.shield.shields import get_shield
from utils.shield.shield_autocomplete import shield_autocomplete
from utils.constants import SHIELD_COLOURS, COLOURED_ELEMENT_EMOJIS, SHIELD_EMOJIS
from utils.icons import get_shield_icon


class Shield(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_element(self, element: str) -> str:
        special = {
            "all_elements": "All Elements",
            "nightsoul": "Nightsoul",
            "lunar": "Lunar Reactions"
        }

        if element in special:
            return special[element]

        emoji_key = (
            element.lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        emoji = SHIELD_EMOJIS.get(emoji_key) or COLOURED_ELEMENT_EMOJIS.get(emoji_key)

        return f"{emoji} {element}" if emoji else element

    def _build_shield_embed(self, shield_id: str):
        data = get_shield(shield_id)

        if data is None:
            return None

        embed = discord.Embed(
            title=data["name"],
            colour=SHIELD_COLOURS[data["colour"]]
        )

        effective = data.get("effective", {})

        embed.add_field(
            name="**Effectiveness**",
            value=" ",
            inline=False
        )

        if effective.get("best"):
            embed.add_field(
                name="Best",
                value="\n".join(
                    f"**{self.format_element(item)}**"
                    for item in effective["best"]
                ) + "\n",
                inline=False
            )

        if effective.get("good"):
            embed.add_field(
                name="Good",
                value="\n".join(
                    f"**{self.format_element(item)}**"
                    for item in effective["good"]
                ) + "\n",
                inline=False
            )

        if data.get("ineffective"):
            embed.add_field(
                name="Ineffective",
                value="\n".join(
                    f"**{self.format_element(item)}**"
                    for item in data["ineffective"]
                ) + "\n\u200b",
                inline=False
            )

        elements = []
        values = []

        for element, value in data["coefficient"].items():
            elements.append(f"**{self.format_element(element)}**")

            if value is None:
                values.append("—")
            elif isinstance(value, (int, float)):
                values.append(f"×**{value}U**")
            else:
                values.append(str(value))

        embed.add_field(
            name="**Values**",
            value=" ",
            inline=False
        )

        embed.add_field(
            name="Element",
            value="\n".join(elements) + "\n\u200b",
            inline=True
        )

        embed.add_field(
            name="Shield Consumption",
            value="\n".join(values),
            inline=True
        )

        notes = "\n".join(data["notes"])

        if len(notes) <= 1024:
            embed.add_field(
                name="**Notes**",
                value=notes,
                inline=False
            )
        else:
            split = notes.rfind("\n", 0, 1024)

            embed.add_field(
                name="**Notes**",
                value=notes[:split],
                inline=False
            )

            embed.add_field(
                name="**Notes (continuation)**",
                value=notes[split + 1:],
                inline=False
            )

        icon = discord.File(
            get_shield_icon(data["emoji"]),
            filename="shield.png"
        )

        embed.set_image(
            url=f"attachment://shield.png"
        )

        return embed, icon

    @app_commands.command(
        name="shield",
        description="Shows information about a shield."
    )
    @app_commands.describe(
        shield="The shield to view."
    )
    @app_commands.autocomplete(shield=shield_autocomplete)
    async def shield(
            self,
            interaction: discord.Interaction,
            shield: str
    ):
        result = self._build_shield_embed(shield.lower())

        if result is None:
            await interaction.response.send_message(
                "Shield not found.",
                ephemeral=True
            )
            return

        embed, icon = result

        if embed is None:
            await interaction.response.send_message(
                "Shield not found.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=embed,
            file=icon
        )

    @commands.command(
        name="shield",
        aliases=["sh"]
    )
    async def shield_prefix(self, ctx, shield: str):
        if shield is None:
            await ctx.send(
                "Please specify a shield.\nExample: `?shield pyro`"
            )
            return

        result = self._build_shield_embed(shield.lower())

        if result is None:
            await ctx.send("Shield not found.")
            return

        embed, icon = result

        if embed is None:
            await ctx.send("Shield not found.")
            return

        await ctx.send(
            embed=embed,
            file=icon
        )


async def setup(bot):
    await bot.add_cog(Shield(bot))