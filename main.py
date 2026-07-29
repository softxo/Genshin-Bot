import discord
import asyncio
import os
import traceback
from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv
from utils.character.character_loader import load_characters, CHARACTERS
from utils.weapon.weapons import load_weapons, get_weapon

load_characters()
load_weapons()

print(get_weapon("raven_bow"))

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print(f"Loaded {len(CHARACTERS)} characters:")
print(list(CHARACTERS.keys()))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="?",
    intents=intents
)

@bot.event
async def setup_hook():
    bot.application_emojis = await bot.fetch_application_emojis()
    print(f"Loaded {len(bot.application_emojis)} application emojis")

async def load_cogs():
    for commands_file in Path("cogs").rglob("commands.py"):
        module = ".".join(commands_file.with_suffix("").parts)

        try:
            await bot.load_extension(module)
            print(f"Loaded cog: {module}")
        except Exception as e:
            print(f"Failed to load cog: {module}: {e}")
            traceback.print_exc()


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="I could really use a wish right now"
        )
    )

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
    traceback.print_exception(type(error), error, error.__traceback__)

if __name__ == "__main__":
    asyncio.run(main())
