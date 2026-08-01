import discord
from discord.ext import commands


class Mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        if self.bot.user in message.mentions:
            await message.reply(
                "Hello! 👋"
            )


async def setup(bot):
    await bot.add_cog(Mention(bot))