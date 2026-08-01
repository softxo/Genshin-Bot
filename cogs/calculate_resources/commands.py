import discord
from discord.ext import commands
from discord import app_commands
from utils.character.characters import get_character
from utils.resource_calculator import calculate_character_resources
from utils.character.character_autocomplete import character_autocomplete
from utils.weapon.weapon_autocomplete import weapon_autocomplete
from utils.icons import get_material_emoji, get_character_icon, get_character_splash
from utils.materials.materials import GEMS, BOSSES, LOCAL_SPECIALTIES, COMMON, MISC
from utils.constants.emojis import COLOURED_ELEMENT_EMOJIS


def format_resource_embed(
        character: dict,
        resources: dict,
        emojis
) -> tuple[discord.Embed, discord.File, discord.File]:

    levels = resources["levels"]
    exp = resources["exp"]
    books = exp["books"]
    ascension = resources["ascension"]
    mora = resources["mora"]

    mora_data = MISC["mora"]

    exp_emoji = get_material_emoji(
        emojis,
        "Character_EXP"
    )

    wasted_exp_emoji = get_material_emoji(
        emojis,
        "Wasted_Character_EXP"
    )

    element_emoji = COLOURED_ELEMENT_EMOJIS.get(
        character["element"].lower()
    )

    embed = discord.Embed(
        title=f"Resource Calculator • {character['name']}",
        colour=discord.Colour.from_str(character["colour"])
    )

    embed.add_field(
        name="Character",
        value=f"{element_emoji} **{character['name']}**",
        inline=True
    )

    embed.add_field(
        name="Starting Level",
        value=str(levels["starting"]),
        inline=True
    )

    embed.add_field(
        name="Target Level",
        value=str(levels["ending"]),
        inline=True
    )

    embed.add_field(
        name=" ",
        value=" ",
        inline=False
    )
    embed.add_field(
        name="EXP",
        value=(
            f"{exp_emoji} **Required:** {exp['required']:,}\n"
            f"{wasted_exp_emoji} **Wasted:** {exp['wasted']:,}"
        ) + "\n\u200b",
        inline=False
    )

    level_lines = []

    for book_id in (
            "heros_wit",
            "adventurers_experience",
            "wanderers_advice"
    ):
        amount = books.get(book_id, 0)

        if amount <= 0:
            continue

        book = MISC[book_id]

        emoji = get_material_emoji(
            emojis,
            book["emoji"]
        )

        level_lines.append(
            f"{emoji} **{book['name']}** ×{amount}"
        )

    embed.add_field(
        name="Level Materials",
        value="\n".join(level_lines)+ "\n\u200b",
        inline=False
    )

    ascension_lines = []

    gem_id = ascension["gem"]["id"]
    gem = GEMS[gem_id]

    for tier in (
        "sliver",
        "fragment",
        "chunk",
        "gemstone"
    ):
        amount = ascension["gem"].get(tier, 0)

        if amount <= 0:
            continue

        emoji = get_material_emoji(
            emojis,
            gem["tiers"][tier]["emoji"]
        )

        ascension_lines.append(
            f"{emoji} **{gem['tiers'][tier]['name']}** ×{amount}"
        )

    ascension_lines.append("")

    boss_id = ascension["boss"]["id"]
    boss = BOSSES[boss_id]

    boss_emoji = get_material_emoji(
        emojis,
        boss["emoji"]
    )

    ascension_lines.append(
        f"{boss_emoji} **{boss['name']}** ×{ascension['boss']['amount']}"
    )

    ascension_lines.append("")

    local_id = ascension["local_specialty"]["id"]
    local = LOCAL_SPECIALTIES[local_id]

    local_emoji = get_material_emoji(
        emojis,
        local["emoji"]
    )

    ascension_lines.append(
        f"{local_emoji} **{local['name']}** ×{ascension['local_specialty']['amount']}"
    )

    ascension_lines.append("")

    common_id = ascension["common"]["id"]
    common = COMMON[common_id]

    for tier in (
        "tier1",
        "tier2",
        "tier3"
    ):
        amount = ascension["common"].get(tier, 0)

        if amount <= 0:
            continue

        emoji = get_material_emoji(
            emojis,
            common["tiers"][tier]["emoji"]
        )

        ascension_lines.append(
            f"{emoji} **{common['tiers'][tier]['name']}** ×{amount}"
        )

    embed.add_field(
        name="Ascension Materials",
        value="\n".join(ascension_lines) + "\n\u200b",
        inline=False
    )

    mora_emoji = get_material_emoji(
        emojis,
        mora_data["emoji"]
    )

    embed.add_field(
        name="Mora",
        value=(
            f"{mora_emoji} **{mora_data['name']}** ×{mora['levelling']:,} → **Level**\n\u200b"
            f"{mora_emoji} **{mora_data['name']}** ×{mora['ascension']:,} → **Ascension**\n\u200b"
            f"{mora_emoji} **{mora_data['name']}** ×{mora['total']:,} →**Total**"
        ),
        inline=False
    )

    character_icon = discord.File(
        get_character_icon(character["id"]),
        filename="character.png"
    )

    character_splash = discord.File(
        get_character_splash(character["id"]),
        filename="splash.png"
    )

    embed.set_thumbnail(url="attachment://character.png")
    embed.set_image(url="attachment://splash.png")

    return embed, character_icon, character_splash


async def resource_name_autocomplete(
        interaction: discord.Interaction,
        current: str,
):
    category = interaction.namespace.category

    if isinstance(category, app_commands.Choice):
        category = category.value

    if category == "character":
        return await character_autocomplete(
            interaction,
            current
        )

    if category == "weapon":
        return await weapon_autocomplete(
            interaction,
            current
        )

    return []


class CalculateResources(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="calculateresources",
        description="Calculate resources needed to level a character or weapon."
    )
    @app_commands.choices(
        category=[
            app_commands.Choice(name="Character", value="character"),
            app_commands.Choice(name="Weapon", value="weapon"),
        ]
    )
    @app_commands.autocomplete(name=resource_name_autocomplete)
    async def calculate_resources(
        self,
        interaction: discord.Interaction,
        category: app_commands.Choice[str],
        name: str,
        starting_level: app_commands.Range[int, 1, 90],
        end_level: app_commands.Range[int, 1, 90],
    ):

        if starting_level >= end_level:
            await interaction.response.send_message(
                "The starting level must be lower than the end level.",
                ephemeral=True
            )
            return

        if category.value == "weapon":
            await interaction.response.send_message(
                "Weapon resource calculation isn't implemented yet.",
                ephemeral=True
            )
            return

        character = get_character(name)

        if character is None:
            await interaction.response.send_message(
                f"Character `{name}` could not be found.",
                ephemeral=True
            )
            return

        resources = calculate_character_resources(
            character,
            starting_level,
            end_level
        )

        embed, character_icon, character_splash = format_resource_embed(
            character,
            resources,
            self.bot.application_emojis
        )

        await interaction.response.send_message(
            embed=embed,
            files=[character_icon, character_splash]
        )

    @commands.command(
        name="calculateresources",
        aliases=["cr"]
    )
    async def calculate_resources_prefix(
            self,
            ctx,
            category: str,
            name: str,
            starting_level: int,
            end_level: int,
    ):
        if starting_level < 1 or end_level > 90:
            await ctx.send(
                "Levels must be between 1 and 90."
            )
            return

        if starting_level >= end_level:
            await ctx.send(
                "The starting level must be lower than the end level."
            )
            return

        if category.lower() == "weapon":
            await ctx.send(
                "Weapon resource calculation isn't implemented yet."
            )
            return

        if category.lower() != "character":
            await ctx.send(
                "Category must be `Character` or `Weapon`."
            )
            return

        character = get_character(name)

        if character is None:
            await ctx.send(
                f"Character `{name}` could not be found."
            )
            return

        resources = calculate_character_resources(
            character,
            starting_level,
            end_level
        )

        embed, character_icon, character_splash = format_resource_embed(
            character,
            resources,
            self.bot.application_emojis
        )

        await ctx.send(
            embed=embed,
            files=[character_icon, character_splash]
        )

async def setup(bot):
    await bot.add_cog(CalculateResources(bot))