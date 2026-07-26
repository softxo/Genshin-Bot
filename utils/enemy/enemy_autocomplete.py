from discord import app_commands
from utils.enemy.enemies import ENEMIES


async def enemy_autocomplete(
    interaction,
    current: str
):
    current = current.lower()

    results = []

    for enemy_id, data in ENEMIES.items():

        name = data["name"]

        if current in enemy_id.lower() or current in name.lower():

            results.append(
                app_commands.Choice(
                    name=name,
                    value=enemy_id
                )
            )

        if len(results) >= 25:
            break

    return results