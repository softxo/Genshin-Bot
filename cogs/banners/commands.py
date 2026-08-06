import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone, timedelta
from utils.banners.banners import get_current_banner
from utils.character.characters import get_character
from utils.constants.emojis import COLOURED_ELEMENT_EMOJIS


SERVER_OFFSETS = {
    "NA": -5,
    "EU": 1,
    "AS": 8,
}


class Banners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _build_banner(self):
        banner = get_current_banner()

        version = banner["version"]
        phase = banner["phase"]

        embed = discord.Embed(
            title=f"Version {version} | {phase}",
            colour=discord.Colour.gold()
        )

        banner_file = discord.File(
            "assets/banners/6.7_second_half.gif",
            filename="banner_6.7_2.gif"
        )

        embed.set_image(
            url="attachment://banner_6.7_2.gif"
        )

        embed.set_footer(
            text="The times are converted to match your timezone."
        )

        five_star_lines = []

        for character_id in banner["characters"]["5_star"]:
            character = get_character(character_id)

            print("BANNER CHARACTER:", character_id)
            print("LOOKUP RESULT:", get_character(character_id))

            if character is None:
                five_star_lines.append(character_id)
                continue

            name = character["name"]
            element = character["element"]

            emoji = COLOURED_ELEMENT_EMOJIS.get(
                element.lower(),
                ""
            )

            five_star_lines.append(
                f"{emoji} **{name}**"
            )

        embed.add_field(
            name="Promotional 5★ Characters",
            value="\n".join(five_star_lines) or "None" + "\n\u200b",
            inline=True
        )

        four_star_lines = []

        for character_id in banner["characters"]["4_star"]:
            character = get_character(character_id)

            if character is None:
                four_star_lines.append(character_id)
                continue

            name = character["name"]
            element = character["element"]

            emoji = COLOURED_ELEMENT_EMOJIS.get(
                element.lower(),
                ""
            )

            four_star_lines.append(
                f"{emoji} **{name}**"
            )

        embed.add_field(
            name="Featured 4★ Characters",
            value="\n".join(four_star_lines) or "None",
            inline=True
        )

        start = datetime.fromisoformat(
            banner["duration"]["start"]
        )

        end = datetime.fromisoformat(
            banner["duration"]["end"]
        )

        duration = (
            f"**{start.strftime('%d/%m/%Y %H:%M')}** - "
            f"**{end.strftime('%d/%m/%Y %H:%M')}** | [UTC+1]"
        )

        embed.add_field(
            name="Duration",
            value=duration + "\n\u200b",
            inline=False
        )

        def regional_timestamp(dt, offset):
            naive = dt.replace(tzinfo=None)

            regional_dt = naive.replace(
                tzinfo=timezone(timedelta(hours=offset))
            )

            return int(regional_dt.timestamp())

        started_lines = []

        for region, offset in SERVER_OFFSETS.items():
            timestamp = regional_timestamp(start, offset)

            started_lines.append(
                f"{region}: <t:{timestamp}:R>"
            )

        embed.add_field(
            name="Started",
            value="\n".join(started_lines),
            inline=True
        )

        ending_lines = []

        for region, offset in SERVER_OFFSETS.items():
            timestamp = regional_timestamp(end, offset)

            ending_lines.append(
                f"{region}: <t:{timestamp}:R>"
            )

        embed.add_field(
            name="Ending",
            value="\n".join(ending_lines),
            inline=True
        )

        return embed, banner_file

    @app_commands.command(
        name="banners",
        description="Shows the current character event banners."
    )
    async def banners(self, interaction: discord.Interaction):

        embed, banner_file = self._build_banner()

        await interaction.response.send_message(
            embed=embed,
            file=banner_file
        )

    @commands.command(
        name="banners"
    )
    async def banners_prefix(self, ctx):

        embed, banner_file = self._build_banner()

        await ctx.send(
            embed=embed,
            file=banner_file
        )


async def setup(bot):
    await bot.add_cog(Banners(bot))