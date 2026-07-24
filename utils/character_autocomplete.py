from discord import app_commands
from utils.characters import search_characters
from utils.loader import CHARACTERS


async def character_autocomplete(
    interaction,
    current: str
):
    choices = []

    for char_id in search_characters(current):
        choices.append(
            app_commands.Choice(
                name=CHARACTERS[char_id]["name"],
                value=char_id
            )
        )

    return choices