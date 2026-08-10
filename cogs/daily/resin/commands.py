import discord
import time
from pathlib import Path
from discord import app_commands
from discord.ext import commands
from utils.hoyolab.account_client import get_account_client
from utils.hoyolab.database import get_accounts
from utils.hoyolab.daily_note import get_resin
from utils.errors.error_handler import create_error_embed


def format_duration(seconds: int) -> str:
    seconds = max(0, int(seconds))

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    if seconds or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


async def _get_resin_message(
    user_id: int,
    account: dict
):
    try:
        client = get_account_client(
            user_id,
            account["genshin_uid"]
        )

        if client is None:
            embed = create_error_embed(
                "Account Not Found",
                "The linked Genshin account could not be found.",
                "not_found"
            )

            return embed, None

        async with client:
            response = await client.get_genshin_daily_note(
                client.genshin_uid,
                client.genshin_server
            )

        current_resin, max_resin, recovery = get_resin(
            response
        )

        if current_resin >= max_resin:
            replenished_in = "Full"
            fully_replenished = "Full"

        else:
            remaining_resin = max_resin - current_resin

            fully_replenished_seconds = recovery

            next_resin_seconds = (
                fully_replenished_seconds
                - ((remaining_resin - 1) * 480)
            )

            next_resin_timestamp = (
                int(time.time()) + next_resin_seconds
            )

            replenished_in = (
                f"<t:{next_resin_timestamp}:R>"
            )

            fully_replenished_timestamp = (
                int(time.time())
                + fully_replenished_seconds
            )

            fully_replenished = (
                f"<t:{fully_replenished_timestamp}:R>"
            )

    except Exception:
        embed = create_error_embed(
            "Failed to Retrieve Resin",
            "Cyrene couldn't retrieve your Genshin Resin data from HoYoLAB.",
            "error"
        )

        return embed, None

    resin_image = Path(
        "assets/hoyolab/daily/Original_Resin.webp"
    )

    file = discord.File(
        resin_image,
        filename="Original_Resin.webp"
    )

    embed = discord.Embed(
        title="Resin",
        colour=discord.Colour.blurple()
    )

    embed.set_thumbnail(
        url="attachment://Original_Resin.webp"
    )

    embed.add_field(
        name="Account",
        value=(
            f"- **Name**: {account.get('nickname', 'Unknown')}\n"
            f"- **UID**: {account['genshin_uid']}\n"
            f"- **AR**: {account.get('level', 'Unknown')}"
        ) + "\n\u200b",
        inline=False
    )

    embed.add_field(
        name="Resin",
        value=(
            f"- **Current**: {current_resin}/{max_resin}\n"
            f"- **Replenished**: {replenished_in}\n"
            f"- **Fully Replenished**: {fully_replenished}"
        ),
        inline=False
    )

    return embed, file


def create_account_options(
    accounts: list[dict]
) -> list[discord.SelectOption]:
    options = []

    for account in accounts:
        options.append(
            discord.SelectOption(
                label=(
                    account.get("nickname")
                    or account["genshin_uid"]
                ),
                description=(
                    f"UID: {account['genshin_uid']}"
                    + (
                        f" • AR: {account['level']}"
                        if account.get("level") is not None
                        else ""
                    )
                ),
                value=account["genshin_uid"]
            )
        )

    return options


class ResinAccountSelect(discord.ui.Select):
    def __init__(
        self,
        discord_user_id: int,
        options: list[discord.SelectOption]
    ):
        super().__init__(
            placeholder="Select a Genshin Account...",
            options=options
        )

        self.discord_user_id = discord_user_id

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        genshin_uid = self.values[0]

        accounts = get_accounts(
            self.discord_user_id
        )

        account = next(
            (
                account
                for account in accounts
                if account["genshin_uid"] == genshin_uid
            ),
            None
        )

        if account is None:
            embed = create_error_embed(
                "Account Not Found",
                "The selected Genshin account could not be found.",
                "not_found"
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        await interaction.response.defer()

        embed, file = await _get_resin_message(
            self.discord_user_id,
            account
        )

        if file is not None:
            await interaction.edit_original_response(
                embed=embed,
                attachments=[file]
            )
        else:
            await interaction.edit_original_response(
                embed=embed,
                attachments=[]
            )


class ResinAccountView(discord.ui.View):
    def __init__(
        self,
        discord_user_id: int,
        options: list[discord.SelectOption]
    ):
        super().__init__(
            timeout=600
        )

        self.add_item(
            ResinAccountSelect(
                discord_user_id,
                options
            )
        )


class Resin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _show_resin(
        self,
        user_id: int,
        accounts: list[dict],
        *,
        interaction: discord.Interaction | None = None,
        ctx: commands.Context | None = None,
        ephemeral: bool = True
    ):
        account = accounts[0]

        embed, file = await _get_resin_message(
            user_id,
            account
        )

        view = None

        if len(accounts) > 1:
            view = ResinAccountView(
                user_id,
                create_account_options(accounts)
            )

        if interaction:
            await interaction.followup.send(
                embed=embed,
                file=file,
                view=view,
                ephemeral=ephemeral
            )

        else:
            await ctx.send(
                embed=embed,
                file=file,
                view=view
            )

    @app_commands.command(
        name="resin",
        description="Check your Resin."
    )
    async def resin(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(
            ephemeral=True
        )

        accounts = get_accounts(
            interaction.user.id
        )

        if not accounts:
            embed = create_error_embed(
                "No HoYoLAB Account Linked",
                (
                    "You don't currently have a Genshin account linked to Cyrene.\n\n"
                    "Use `/accounts` to link one."
                ),
                "not_found"
            )

            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )

            return

        await self._show_resin(
            interaction.user.id,
            accounts,
            interaction=interaction,
            ephemeral=True
        )

    @commands.command(
        name="resin"
    )
    async def resin_prefix(
        self,
        ctx: commands.Context
    ):
        accounts = get_accounts(
            ctx.author.id
        )

        if not accounts:
            embed = create_error_embed(
                "No HoYoLAB Account Linked",
                (
                    "You don't currently have a Genshin account linked to Cyrene.\n\n"
                    "Use `/accounts` to link one."
                ),
                "not_found"
            )

            await ctx.send(
                embed=embed
            )

            return

        await self._show_resin(
            ctx.author.id,
            accounts,
            ctx=ctx,
            ephemeral=False
        )


async def setup(bot):
    await bot.add_cog(Resin(bot))