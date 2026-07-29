import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="purge",
        description="Deletes a number of messages."
    )
    @commands.has_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if not 1 <= amount <= 100:
            await ctx.send("Amount must be between **1** and **100**.")
            return

        embed = discord.Embed(
            description=f"Deleting **{amount}** message(s)...",
            colour=discord.Colour.orange()
        )

        status = await ctx.send(embed=embed)

        if ctx.interaction is None:
            await ctx.message.delete()

        deleted = await ctx.channel.purge(
            limit=amount,
            before=status
        )

        embed = discord.Embed(
            description=f"Deleted **{len(deleted)}** message(s).",
            colour=discord.Colour.green()
        )

        await status.edit(embed=embed)
        await status.delete(delay=3)

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I need the **Manage Messages** permission.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `?purge <amount>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("The amount must be a whole number.")



async def setup(bot):
    await bot.add_cog(Utility(bot))