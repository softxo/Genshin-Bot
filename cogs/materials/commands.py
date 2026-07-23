import discord
from discord.ext import commands
from discord import app_commands
from utils.characters import get_character
from utils.autocomplete import character_autocomplete
from utils.icons import get_character_icon, get_material_emoji
from utils.constants import ASCENSION_MORA_COSTS, ASCENSION_EXP_COSTS, TALENT_MORA_COSTS

import json
from pathlib import Path

MATERIALS_PATH = Path("data/materials")


def load_json(filename):
    with open(
        MATERIALS_PATH / filename,
        encoding="utf-8"
    ) as f:
        return json.load(f)


GEMS = load_json("gems.json")
BOOKS = load_json("books.json")
COMMON = load_json("common.json")
BOSSES = load_json("boss.json")
WEEKLY = load_json("weekly.json")
LOCAL_SPECIALTIES = load_json("local_specialties.json")
MISC = load_json("miscellaneous.json")
ASCENSION_MORA_TOTAL = sum(ASCENSION_MORA_COSTS)
SINGLE_TALENT_MORA_TOTAL = sum(TALENT_MORA_COSTS)
ALL_TALENTS_MORA_TOTAL = 3 * sum(TALENT_MORA_COSTS)


def get_ascension_text(data, emojis):
    materials = data["materials"]
    ascension = materials["ascension"]

    gem = GEMS[ascension["gem"]["id"]]
    boss = BOSSES[ascension["boss"]["id"]]
    local = LOCAL_SPECIALTIES[ascension["local_specialty"]["id"]]
    common = COMMON[ascension["common"]["id"]]

    gem_sliver_emoji = get_material_emoji(emojis, gem["tiers"]["sliver"]["emoji"])
    gem_fragment_emoji = get_material_emoji(emojis, gem["tiers"]["fragment"]["emoji"])
    gem_chunk_emoji = get_material_emoji(emojis, gem["tiers"]["chunk"]["emoji"])
    gem_gemstone_emoji = get_material_emoji(emojis, gem["tiers"]["gemstone"]["emoji"])

    boss_emoji = get_material_emoji(emojis, boss["emoji"])
    local_emoji = get_material_emoji(emojis, local["emoji"])

    common_tier1_emoji = get_material_emoji(emojis, common["tiers"]["tier1"]["emoji"])
    common_tier2_emoji = get_material_emoji(emojis, common["tiers"]["tier2"]["emoji"])
    common_tier3_emoji = get_material_emoji(emojis, common["tiers"]["tier3"]["emoji"])

    return (
        f"{gem_sliver_emoji} **{gem['tiers']['sliver']['name']}** ×{ascension['gem']['sliver']}\n"
        f"{gem_fragment_emoji} **{gem['tiers']['fragment']['name']}** ×{ascension['gem']['fragment']}\n"
        f"{gem_chunk_emoji} **{gem['tiers']['chunk']['name']}** ×{ascension['gem']['chunk']}\n"
        f"{gem_gemstone_emoji} **{gem['tiers']['gemstone']['name']}** ×{ascension['gem']['gemstone']}\n\n"
        
        f"{boss_emoji} **{boss['name']}** ×{ascension['boss']['amount']}\n\n"

        f"{local_emoji} **{local['name']}** ×{ascension['local_specialty']['amount']}\n\n"

        f"{common_tier1_emoji} **{common['tiers']['tier1']['name']}** ×{ascension['common']['tier1']}\n"
        f"{common_tier2_emoji} **{common['tiers']['tier2']['name']}** ×{ascension['common']['tier2']}\n"
        f"{common_tier3_emoji} **{common['tiers']['tier3']['name']}** ×{ascension['common']['tier3']}"
    )

def get_ascension_misc_text(emojis):
    mora = MISC["mora"]
    wit = MISC["heros_wit"]
    adventure = MISC["adventurers_experience"]
    wanderer = MISC["wanderers_advice"]

    mora_emoji = get_material_emoji(emojis, mora["emoji"])
    wit_emoji = get_material_emoji(emojis, wit["emoji"])
    adventure_emoji = get_material_emoji(emojis, adventure["emoji"])
    wanderer_emoji = get_material_emoji(emojis, wanderer["emoji"])

    return (
        f"{mora_emoji} **{mora['name']}** ×{ASCENSION_MORA_TOTAL:,}\n"
        f"{wit_emoji} **{wit['name']}** ×{ASCENSION_EXP_COSTS['heros_wit']:,}\n"
        f"{adventure_emoji} **{adventure['name']}** ×{ASCENSION_EXP_COSTS['adventurers_experience']}\n"
        f"{wanderer_emoji} **{wanderer['name']}** ×{ASCENSION_EXP_COSTS['wanderers_advice']}"
    )

def build_ascension_embed(data, emojis):
    embed = discord.Embed(
        title=f"{data['name']} • Ascension Materials",
        colour=discord.Colour.from_str(data["colour"])
    )

    embed.set_thumbnail(url="attachment://character.png")

    embed.add_field(
        name="Character Ascension (Lv. 1 → 90)",
        value=get_ascension_text(data, emojis) + "\n\u200b",
        inline=False
    )

    embed.add_field(
        name="Character Levels",
        value=get_ascension_misc_text(emojis),
        inline=False
    )

    return embed


def get_talent_text(data, emojis):
    materials = data["materials"]
    talents = materials["talents"]

    book = BOOKS[talents['book']['id']]
    common = COMMON[talents['common']['id']]
    weekly = WEEKLY[talents['weekly_boss']['id']]
    weekly_drop = weekly["drops"][talents["weekly_boss"]["material"]]
    crown = MISC[talents["crown"]["id"]]

    book_tier1_emoji = get_material_emoji(emojis, book["tiers"]["teachings"]["emoji"])
    book_tier2_emoji = get_material_emoji(emojis, book["tiers"]["guide"]["emoji"])
    book_tier3_emoji = get_material_emoji(emojis, book["tiers"]["philosophies"]["emoji"])

    common_tier1_emoji = get_material_emoji(emojis, common["tiers"]["tier1"]["emoji"])
    common_tier2_emoji = get_material_emoji(emojis, common["tiers"]["tier2"]["emoji"])
    common_tier3_emoji = get_material_emoji(emojis, common["tiers"]["tier3"]["emoji"])

    weekly_emoji = get_material_emoji(emojis, weekly["emoji"])
    weekly_drop_emoji = get_material_emoji(emojis, weekly_drop["emoji"])

    crown_emoji = get_material_emoji(emojis, crown["emoji"])

    return (
        f"{book_tier1_emoji} **{book['tiers']['teachings']['name']}** ×{talents['book']['teachings'] // 3}\n"
        f"{book_tier2_emoji} **{book['tiers']['guide']['name']}** ×{talents['book']['guide'] // 3}\n"
        f"{book_tier3_emoji} **{book['tiers']['philosophies']['name']}** ×{talents['book']['philosophies'] // 3}\n\n"

        f"{common_tier1_emoji} **{common['tiers']['tier1']['name']}** ×{talents['common']['tier1'] // 3}\n"
        f"{common_tier2_emoji} **{common['tiers']['tier2']['name']}** ×{talents['common']['tier2'] // 3}\n"
        f"{common_tier3_emoji} **{common['tiers']['tier3']['name']}** ×{talents['common']['tier3'] // 3}\n\n"

        f"{weekly_drop_emoji} **{weekly_drop['name']}** ×{talents['weekly_boss']['amount'] // 3}\n\n"
        
        f"{crown_emoji} **{crown['name']}** ×{talents['crown']['amount'] // 3}"
    )

def get_talent_misc_text(emojis):
    mora = MISC["mora"]

    mora_emoji = get_material_emoji(emojis, mora["emoji"])

    return (
        f"{mora_emoji} **{mora['name']}** ×{SINGLE_TALENT_MORA_TOTAL:,}"
    )

def build_talents_embed(data, emojis):
    embed = discord.Embed(
        title=f"{data['name']} • Talent Materials",
        colour=discord.Colour.from_str(data["colour"])
    )

    embed.set_thumbnail(url="attachment://character.png")

    embed.add_field(
        name="Cost per Talent (Lv. 1 → 10)",
        value=get_talent_text(data, emojis) + "\n\u200b",
        inline=False
    )

    embed.add_field(
        name="Mora",
        value=get_talent_misc_text(emojis),
        inline=False
    )

    return embed


def get_total_extras_text(emojis):
    mora = MISC["mora"]
    wit = MISC["heros_wit"]
    adventure = MISC["adventurers_experience"]
    wanderer = MISC["wanderers_advice"]

    mora_emoji = get_material_emoji(emojis, mora["emoji"])
    wit_emoji = get_material_emoji(emojis, wit["emoji"])
    adventure_emoji = get_material_emoji(emojis, adventure["emoji"])
    wanderer_emoji = get_material_emoji(emojis, wanderer["emoji"])

    total_mora = ASCENSION_MORA_TOTAL + SINGLE_TALENT_MORA_TOTAL

    return (
        f"{mora_emoji} **{mora['name']}** ×{total_mora:,}\n"
        f"{wit_emoji} **{wit['name']}** ×{ASCENSION_EXP_COSTS['heros_wit']:,}\n"
        f"{adventure_emoji} **{adventure['name']}** ×{ASCENSION_EXP_COSTS['adventurers_experience']}\n"
        f"{wanderer_emoji} **{wanderer['name']}** ×{ASCENSION_EXP_COSTS['wanderers_advice']}"
    )

def build_total_embed(data, emojis):
    embed = discord.Embed(
        title=f"{data['name']} • Total Materials",
        colour=discord.Colour.from_str(data["colour"])
    )

    embed.set_thumbnail(url="attachment://character.png")

    embed.add_field(
        name="Character Ascension (Lv. 1 → 90)",
        value=get_ascension_text(data, emojis) + "\n\u200b",
        inline=False
    )

    embed.add_field(
        name="Cost per Talent (Lv. 1 → 10)",
        value=get_talent_text(data, emojis) + "\n\u200b",
        inline=False
    )

    embed.add_field(
        name="Other Materials",
        value=get_total_extras_text(emojis),
        inline=False
    )
    return embed

class MaterialsView(discord.ui.View):
    def __init__(self, data, emojis, user_id):
        super().__init__(timeout=300)

        self.user_id = user_id

        self.ascension_embed = build_ascension_embed(data, emojis)
        self.talent_embed = build_talents_embed(data, emojis)
        self.total_embed = build_total_embed(data, emojis)

        self.ascension_button = discord.ui.Button(
            label="← Ascension",
            style=discord.ButtonStyle.secondary
        )

        self.talents_button = discord.ui.Button(
            label="Talent →",
            style=discord.ButtonStyle.secondary
        )

        self.total_button = discord.ui.Button(
            label="Total →",
            style=discord.ButtonStyle.secondary
        )

        self.ascension_button.callback = self.ascension_callback
        self.talents_button.callback = self.talents_callback
        self.total_button.callback = self.total_callback

    async def ascension_callback(self, interaction):
        await self.change_page(
            interaction,
            self.ascension_embed,
            "ascension"
        )

    async def talents_callback(self, interaction):
        await self.change_page(
            interaction,
            self.talent_embed,
            "talents"
        )

    async def total_callback(self, interaction):
        await self.change_page(
            interaction,
            self.total_embed,
            "total"
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot control this menu.",
                ephemeral=True
            )
            return False

        return True


    def refresh_thumbnail(self, embed):
        embed.set_thumbnail(
            url="attachment://character.png"
        )
        return embed


    def show_ascension_buttons(self):
        self.clear_items()

        button = discord.ui.Button(
            label="Talent →",
            style=discord.ButtonStyle.secondary
        )

        button.callback = self.talents_callback

        self.add_item(button)


    def show_talent_buttons(self):
        self.clear_items()

        ascension = discord.ui.Button(
            label="← Ascension",
            style=discord.ButtonStyle.secondary
        )

        total = discord.ui.Button(
            label="Total →",
            style=discord.ButtonStyle.secondary
        )

        ascension.callback = self.ascension_callback
        total.callback = self.total_callback

        self.add_item(ascension)
        self.add_item(total)


    def show_total_buttons(self):
        self.clear_items()

        button = discord.ui.Button(
            label="← Talent",
            style=discord.ButtonStyle.secondary
        )

        button.callback = self.talents_callback

        self.add_item(button)


    async def change_page(self, interaction, embed, page):
        if page == "ascension":
            self.show_ascension_buttons()

        elif page == "talents":
            self.show_talent_buttons()

        elif page == "total":
            self.show_total_buttons()

        await interaction.response.edit_message(
            embed=self.refresh_thumbnail(embed),
            view=self
        )



class Materials(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="materials",
        description="Shows a character's Ascension and Talent materials."
    )
    @app_commands.autocomplete(character=character_autocomplete)
    async def materials(
        self,
        interaction: discord.Interaction,
        character: str
    ):
        data = get_character(character)

        if not data:
            await interaction.response.send_message(
                "Character not found.",
                ephemeral=True
            )
            return

        thumbnail = discord.File(
            get_character_icon(data["id"]),
            filename="character.png"
        )

        view = MaterialsView(
            data,
            self.bot.application_emojis,
            interaction.user.id
        )

        view.show_ascension_buttons()

        await interaction.response.send_message(
            embed=view.ascension_embed,
            file=thumbnail,
            view=view
        )

async def setup(bot):
    await bot.add_cog(Materials(bot))
