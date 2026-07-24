import discord
import asyncio
import os
from discord.ext import commands
from dotenv import load_dotenv
from utils.loader import load_characters, CHARACTERS
from utils.weapons import load_weapons, get_weapon

load_characters()
load_weapons()

print(get_weapon("raven_bow"))

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print(f"Loaded {len(CHARACTERS)} characters:")
print(list(CHARACTERS.keys()))

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="?",
    intents=intents
)

@bot.event
async def setup_hook():
    bot.application_emojis = await bot.fetch_application_emojis()
    print(f"Loaded {len(bot.application_emojis)} application emojis")

async def load_cogs():
    for folder in os.listdir("cogs"):
        path = os.path.join("cogs", folder)

        if os.path.isdir(path) and not folder.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{folder}.commands")
                print(f"Loaded cog: {folder}")
            except Exception as e:
                print(f"Failed to load cog {folder}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    for cmd in bot.tree.get_commands():
        print("COMMAND:", cmd.name)

        if cmd.name == "constellations":
            for option in cmd.parameters:
                print(
                    "OPTION:",
                    option.name,
                    "autocomplete:",
                    option.autocomplete
                )

    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s).")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

@bot.tree.error
async def on_app_command_error(interaction, error):
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)

if __name__ == "__main__":
    asyncio.run(main())
