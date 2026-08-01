import discord
import asyncio
import os
import traceback
from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv
from utils.character.character_loader import load_characters, CHARACTERS
from utils.weapon.weapons import load_weapons, WEAPONS
from utils.settings.prefix import get_prefix

load_characters()
load_weapons()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


print("========== Data ==========")
print(f"Loaded {len(CHARACTERS)} character(s):")
print(f"  {', '.join(CHARACTERS)}")

print(f"Loaded {len(WEAPONS)} weapon(s):")
print(f"  {', '.join(WEAPONS)}")
print()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=lambda bot, message: get_prefix(
        message.guild.id if message.guild else None
    ),
    intents=intents,
)


@bot.event
async def setup_hook():
    bot.application_emojis = await bot.fetch_application_emojis()

    print("========= Discord =========")
    print(f"Loaded {len(bot.application_emojis)} application emojis")
    print()

async def load_cogs():
    print("========== Cogs ==========")

    for commands_file in Path("cogs").rglob("*.py"):
        if commands_file.name == "__init__.py":
            continue

        module = ".".join(commands_file.with_suffix("").parts)

        try:
            await bot.load_extension(module)
            print(f"✓ {module}")
        except Exception:
            print(f"✗ {module}")
            traceback.print_exc()

    print()

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="I could really use a wish right now"
        )
    )

    print("========= Ready =========")
    print(f"Logged in as {bot.user}")
    print(f"Guilds: {len(bot.guilds)}")
    print(f"Server Emojis: {len(bot.emojis)}")
    print()


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
        if TOKEN is None:
            raise RuntimeError("DISCORD_TOKEN is not set.")
        await bot.start(TOKEN)


@bot.tree.error
async def on_app_command_error(interaction, error):
    traceback.print_exception(type(error), error, error.__traceback__)

if __name__ == "__main__":
    asyncio.run(main())
