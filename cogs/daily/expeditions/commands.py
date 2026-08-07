import discord
import time
from discord import app_commands
from discord.ext import commands
from utils.hoyolab.account_client import get_account_client
from utils.hoyolab.database import get_accounts
from utils.hoyolab.daily_note import get_expeditions
from utils.errors.error_handler import create_error_embed


async def _send_expeditions(
    user_id: int,
    account: dict,
    *,
    interaction: discord.Interaction | None = None,
    ctx: commands.Context | None = None,
    ephemeral: bool = True
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

            if interaction:
                await interaction.followup.send(
                    embed=embed,
                    ephemeral=ephemeral
                )
            else:
                await ctx.send(
                    embed=embed
                )

            return

        async with client:
            response = await client.get_genshin_daily_note(
                client.genshin_uid,
                client.genshin_server
            )

        expeditions = get_expeditions(
            response
        )

    except Exception:
        embed = create_error_embed(
            "Failed to Retrieve Expeditions",
            "Cyrene couldn't retrieve your Expedition data from HoYoLab.",
            "error"
        )

        if interaction:
            await interaction.followup.send(
                embed=embed,
                ephemeral=ephemeral
            )
        else:
            await ctx.send(
                embed=embed
            )

        return

    finished = sum(
        expedition.get("status") == "Finished"
        for expedition in expeditions
    )

    ongoing = sum(
        expedition.get("status") == "Ongoing"
        for expedition in expeditions
    )

    expedition_lines = []

    for index, expedition in enumerate(
        expeditions,
        start=1
    ):
        status = expedition.get(
            "status",
            "Unknown"
        )

        expedition_timestamp = int(time.time()) + int(
            expedition.get("remained_time", 0)
        )

        remaining_time = f"<t:{expedition_timestamp}:R>"

        if status == "Finished":
            expedition_lines.append(
                f"**{index}.** Finished"
            )

        elif status == "Ongoing":
            expedition_lines.append(
                f"**{index}.** {remaining_time}"
            )

        else:
            expedition_lines.append(
                f"**{index}.** {status}"
            )

    if not expedition_lines:
        expedition_lines.append(
            "No expedition data available."
        )

    embed = discord.Embed(
        title="Expeditions",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Account",
        value=(
            f"- **Name:** {account.get('nickname', 'Unknown')}\n"
            f"- **UID:** {account['genshin_uid']}\n"
            f"- **AR:** {account.get('level', 'Unknown')}"
        ) + "\n\u200b",
        inline=False
    )

    embed.add_field(
        name="Expeditions",
        value=(
            f"- **Finished:** {finished}/{len(expeditions)}\n"
            f"- **Ongoing:** {ongoing}/{len(expeditions)}\n\n"
            + "\n".join(expedition_lines)
        ),
        inline=False
    )

    if interaction:
        await interaction.followup.send(
            embed=embed,
            ephemeral=ephemeral
        )
    else:
        await ctx.send(
            embed=embed
        )


class ExpeditionsAccountSelect(discord.ui.Select):
    def __init__(
        self,
        discord_user_id: int,
        options: list[discord.SelectOption],
        *,
        ephemeral: bool = True
    ):
        super().__init__(
            placeholder="Select a Genshin Account...",
            options=options
        )

        self.discord_user_id = discord_user_id
        self.ephemeral = ephemeral

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
                ephemeral=self.ephemeral
            )

            return

        await interaction.response.defer(
            ephemeral=self.ephemeral
        )

        await _send_expeditions(
            self.discord_user_id,
            account,
            interaction=interaction,
            ephemeral=self.ephemeral
        )


class ExpeditionsAccountView(discord.ui.View):
    def __init__(
        self,
        discord_user_id: int,
        options: list[discord.SelectOption],
        *,
        ephemeral: bool = True
    ):
        super().__init__(
            timeout=300
        )

        self.add_item(
            ExpeditionsAccountSelect(
                discord_user_id,
                options,
                ephemeral=ephemeral
            )
        )


class Expeditions(commands.Cog):
    def __init__(
        self,
        bot
    ):
        self.bot = bot

    @app_commands.command(
        name="expeditions",
        description="Check your Genshin Expeditions."
    )
    async def expeditions(
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
                "No HoYoLab Account Linked",
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

        if len(accounts) == 1:
            await _send_expeditions(
                interaction.user.id,
                accounts[0],
                interaction=interaction,
                ephemeral=True
            )

            return

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

        embed = discord.Embed(
            title="Select a Genshin Account",
            description=(
                "You have multiple linked Genshin accounts.\n"
                "Select the account you want to check."
            ),
            color=discord.Color.blurple()
        )

        await interaction.followup.send(
            embed=embed,
            view=ExpeditionsAccountView(
                interaction.user.id,
                options
            ),
            ephemeral=True
        )

    @commands.command(
        name="expeditions"
    )
    async def expeditions_prefix(
        self,
        ctx: commands.Context
    ):
        accounts = get_accounts(
            ctx.author.id
        )

        if not accounts:
            embed = create_error_embed(
                "No HoYoLab Account Linked",
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

        if len(accounts) == 1:
            await _send_expeditions(
                ctx.author.id,
                accounts[0],
                ctx=ctx
            )

            return

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

        embed = discord.Embed(
            title="Select a Genshin Account",
            description=(
                "You have multiple linked Genshin accounts.\n"
                "Select the account you want to check."
            ),
            color=discord.Color.blurple()
        )

        await ctx.send(
            embed=embed,
            view=ExpeditionsAccountView(
                ctx.author.id,
                options
            )
        )


async def setup(bot):
    await bot.add_cog(Expeditions(bot))