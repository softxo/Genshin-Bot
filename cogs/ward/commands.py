import discord
from discord.ext import commands
from discord import app_commands
from utils.shield.wards import get_ward
from utils.shield.ward_autocomplete import ward_autocomplete
from utils.constants.colours import WARD_COLOURS
from utils.constants.emojis import COLOURED_ELEMENT_EMOJIS, WARD_EMOJIS
from utils.icons import get_ward_icon


class Ward(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_element(self, element: str) -> str:
        lookup = (
            element.lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        special = {
            "all_elements": ("all_elements", "Elemental Damage"),
            "elemental_damage": ("all_elements", "Elemental Damage"),

            "physical_damage": ("physical_damage", "Physical Damage"),

            "nightsoul": ("nightsoul", "Nightsoul"),
            "nightsoul_aligned_attacks": ("nightsoul", "Nightsoul"),

            "lunar": ("lunar", "Lunar Reactions"),

            "phec_+_geo_(crystallize)": (
                "crystallize_reaction",
                "PHEC + Geo (Crystallize)"
            ),
        }

        if lookup in special:
            emoji_key, display = special[lookup]
        else:
            emoji_key = lookup
            display = element.replace("_", " ").title()

        emoji = WARD_EMOJIS.get(emoji_key) or COLOURED_ELEMENT_EMOJIS.get(emoji_key)

        return f"{emoji} {display}" if emoji else display

    def _build_ward_embed(self, ward_id: str):
        data = get_ward(ward_id)

        if data is None:
            return None

        embed = discord.Embed(
            title=data["name"],
            colour=WARD_COLOURS[data["colour"]]
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
            name="Source",
            value="\n".join(elements) + "\n\u200b",
            inline=True
        )

        embed.add_field(
            name="Ward Consumption",
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
            get_ward_icon(data["emoji"]),
            filename="ward.png"
        )

        embed.set_image(
            url=f"attachment://ward.png"
        )

        return embed, icon

    @app_commands.allowed_installs(
        users=True,
        guilds=True
    )
    @app_commands.allowed_contexts(
        guilds=True,
        dms=True,
        private_channels=True
    )
    @app_commands.command(
        name="ward",
        description="Shows information about a ward."
    )
    @app_commands.describe(
        ward="The ward to view."
    )
    @app_commands.autocomplete(ward=ward_autocomplete)
    async def ward(
            self,
            interaction: discord.Interaction,
            ward: str
    ):
        result = self._build_ward_embed(ward.lower())

        if result is None:
            await interaction.response.send_message(
                "Ward not found.",
                ephemeral=True
            )
            return

        embed, icon = result

        await interaction.response.send_message(
            embed=embed,
            file=icon
        )

    @commands.command(
        name="ward",
        aliases=["wd"]
    )
    async def ward_prefix(self, ctx, *, ward: str | None = None):
        if ward is None:
            await ctx.send(
                "Please specify a ward.\nExample: `?ward pyro`"
            )
            return

        result = self._build_ward_embed(ward.lower())

        if result is None:
            await ctx.send("Ward not found.")
            return

        embed, icon = result

        await ctx.send(
            embed=embed,
            file=icon
        )


async def setup(bot):
    await bot.add_cog(Ward(bot))