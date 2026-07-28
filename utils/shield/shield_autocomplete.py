from discord import app_commands

SHIELD_CHOICES = [
    "Pyro",
    "Hydro",
    "Electro",
    "Cryo",
    "Dendro",
    "Geo",
    "Void",
    "Deepdark"
]

async def shield_autocomplete(
    interaction,
    current: str
):
    return [
        app_commands.Choice(name=shield, value=shield.lower())
        for shield in SHIELD_CHOICES
        if current.lower() in shield.lower()
    ][:25]