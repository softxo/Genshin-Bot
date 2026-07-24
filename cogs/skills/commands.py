import discord
from discord.ext import commands
from discord import app_commands
from utils.characters import get_character
from utils.character_autocomplete import character_autocomplete
from utils.icons import get_character_icon, get_talent_emoji
from utils.talents_format import format_description, format_sections

class Skills(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="skills",
        description="Shows a character's Normal, Skill and Burst skills"
    )
    @app_commands.autocomplete(character=character_autocomplete)
    async def skills(
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

        application_emojis = await self.bot.fetch_application_emojis()

        thumbnail = discord.File(
            get_character_icon(data["id"]),
            filename="character.png"
        )

        embed = discord.Embed(
            title=f"{data['name']} • Skills",
            colour=discord.Colour.from_str(data["colour"])
        )

        embed.set_thumbnail(url="attachment://character.png")

        talents = data["talents"]

        # Normal Attack
        normal = talents["normal_attack"]

        embed.add_field(
            name=f"{get_talent_emoji(application_emojis, data['id'], 'normal')} Normal Attack • {normal['name']}",
            value=format_description(normal["description"]) + "\n\u200b",
        )

        # Elemental Skill
        skill = talents["elemental_skill"]

        skill_text = format_description(skill["description"])

        if "sections" in skill:
            skill_text += "\n\n" + format_sections(skill["sections"])

        embed.add_field(
            name=f"{get_talent_emoji(application_emojis, data['id'], 'skill')} Elemental Skill • {skill['name']}",
            value=skill_text + "\n\u200b",
            inline=False
        )

        # Elemental Burst
        burst = talents["elemental_burst"]

        burst_text = format_description(burst["description"])

        if "sections" in burst:
            burst_text += "\n\n" + format_sections(burst["sections"])

        embed.add_field(
            name=f"{get_talent_emoji(application_emojis, data['id'], 'burst')} Elemental Burst • {burst['name']}",
            value=burst_text,
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            file=thumbnail,
        )
        
async def setup(bot):
    await bot.add_cog(Skills(bot))


