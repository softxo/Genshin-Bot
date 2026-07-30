from discord import app_commands
from discord.ext import commands


class Rose(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="wilted_rose",
        aliases=["wilted"]
    )
    async def love_prefix(self, ctx):
        await ctx.send(":wilted_rose:")

    @app_commands.command(
        name="wiltedrose",
        description="Wilted Rose."
    )
    @app_commands.allowed_installs(
        users=True,
        guilds=True
    )
    @app_commands.allowed_contexts(
        guilds=True,
        dms=True,
        private_channels=True
    )
    async def love_slash(self, interaction):
        await interaction.response.send_message(
            ":wilted_rose:"
        )


async def setup(bot):
    await bot.add_cog(Rose(bot))