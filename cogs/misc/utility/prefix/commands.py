import discord
import logging
from discord.ext import commands
from discord import app_commands
from utils.settings.prefix import get_prefix, set_prefix


logger = logging.getLogger(__name__)

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def update_prefix(self, guild_id: int, new_prefix: str):
        if not 1 <= len(new_prefix) <= 5:
            return discord.Embed(
                title="Prefix Error",
                description="Prefix must be between **1** and **5** characters.",
                colour=discord.Colour.red()
            )

        if " " in new_prefix:
            return discord.Embed(
                title="Prefix Error",
                description="The prefix cannot contain spaces.",
                colour=discord.Colour.red()
            )

        old_prefix = get_prefix(guild_id)

        if new_prefix == old_prefix:
            return discord.Embed(
                title="Prefix Error",
                description=f"The prefix is already `{new_prefix}`.",
                colour=discord.Colour.orange()
            )

        set_prefix(guild_id, new_prefix)

        return discord.Embed(
            title="Prefix Updated",
            description=f"**`{old_prefix}`** \u200b → \u200b **`{new_prefix}`**",
            colour=discord.Colour.green()
        )

    @app_commands.command(
        name="prefix",
        description="Changes the bot's prefix."
    )
    @app_commands.describe(
        new_prefix="The new prefix to use."
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.allowed_installs(
        users=True,
        guilds=True
    )
    @app_commands.allowed_contexts(
        guilds=True
    )
    async def prefix_slash(
            self,
            interaction: discord.Interaction,
            new_prefix: str
    ):
        embed = self.update_prefix(
            interaction.guild.id,
            new_prefix
        )

        await interaction.response.send_message(
            embed=embed
        )

    @commands.command(
        name="prefix",
        aliases=["setprefix"]
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix: str):
        embed = self.update_prefix(
            ctx.guild.id,
            new_prefix
        )
        await ctx.send(embed=embed)

    @prefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="You must be an **Administrator** to change the prefix.",
                colour=discord.Colour.red()
            )

            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Missing Argument",
                description=f"Usage: `{get_prefix(ctx.guild.id)}prefix <new prefix>`",
                colour=discord.Colour.red()
            )

            await ctx.send(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(
                title="Guild Only",
                description="This command can only be used in a server.",
                colour=discord.Colour.red()
            )

            await ctx.send(embed=embed)

        else:
            logger.exception("Unexpected error in prefix command")

            embed = discord.Embed(
                title="Unexpected Error",
                description="An unexpected error occurred while executing this command.",
                colour=discord.Colour.red()
            )

            await ctx.send(embed=embed)

    @prefix_slash.error
    async def prefix_slash_error(
            self,
            interaction: discord.Interaction,
            error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions",
                description="You must be an **Administrator** to change the prefix.",
                colour=discord.Colour.red()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        else:
            logger.exception("Unexpected error in slash prefix command")

            embed = discord.Embed(
                title="Unexpected Error",
                description="An unexpected error occurred while executing this command.",
                colour=discord.Colour.red()
            )

            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Prefix(bot))