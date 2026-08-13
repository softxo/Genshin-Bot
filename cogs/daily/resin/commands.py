import discord
import time
from pathlib import Path
from discord import app_commands
from discord.ext import commands
from utils.hoyolab.account_client import get_account_client
from utils.hoyolab.database import (
    get_accounts,
    get_reminders,
    delete_reminder
)
from utils.hoyolab.daily_note import get_resin
from utils.errors.error_handler import create_error_embed
from cogs.reminders.commands import ResinReminderModal
from utils.constants.emojis import (
    HOYOLAB_EMOJIS,
    ERROR_EMOJIS,
    MISC_EMOJIS
)


async def _get_resin_message(
    user_id: int,
    account: dict
):
    try:
        client = await get_account_client(
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

            next_resin_seconds = recovery

            fully_replenished_seconds = (
                    next_resin_seconds
                    + ((remaining_resin - 1) * 480)
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
        import traceback
        traceback.print_exc()

        embed = create_error_embed(
            "Failed to Retrieve Resin",
            "Cyrene couldn't retrieve your Genshin Resin data from HoYoLAB.",
            "error"
        )

        return embed, None

    resin_image = Path(
        "assets/hoyolab/daily/Original_Resin.webp"
    )

    reminders = await get_reminders(
        user_id
    )

    manual_reminder, automatic_reminder = get_resin_reminders(
        reminders,
        account["genshin_uid"]
    )

    manual_status, manual_amount = get_resin_reminder_display(
        manual_reminder
    )

    automatic_status, automatic_amount = get_resin_reminder_display(
        automatic_reminder
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
        ) + "\n\u200b",
        inline=False
    )

    embed.add_field(
        name="Reminders",
        value=(
            "⦁\u2002**Manual Reminder**\n"
            "⦁\u2002**Automatic Reminder**"
        ),
        inline=True
    )

    embed.add_field(
        name="\u200b",
        value=(
            f"{manual_status}\n"
            f"{automatic_status}"
        ),
        inline=True
    )

    embed.add_field(
        name="\u200b",
        value=(
            f"{f'{manual_amount}' if manual_amount else '\u200b'}\n"
            f"{f'{automatic_amount}' if automatic_amount else '\u200b'}"
        ),
        inline=True
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


def get_resin_reminders(
    reminders: list[dict],
    genshin_uid: str
) -> tuple[dict | None, dict | None]:

    manual = next(
        (
            reminder
            for reminder in reminders
            if reminder["genshin_uid"] == genshin_uid
            and reminder["reminder_type"] == "resin"
            and reminder["reminder_mode"] == "manual"
        ),
        None
    )

    automatic = next(
        (
            reminder
            for reminder in reminders
            if reminder["genshin_uid"] == genshin_uid
            and reminder["reminder_type"] == "resin"
            and reminder["reminder_mode"] == "automatic"
        ),
        None
    )

    return manual, automatic


def get_resin_reminder_display(
    reminder: dict | None
) -> tuple[str, str]:

    if reminder is None or not reminder["enabled"]:
        return (
            f"{ERROR_EMOJIS['error']} Disabled",
            "\u200b"
        )

    config = reminder.get("config") or {}

    amount = config.get("amount")

    status = (
        f"{ERROR_EMOJIS['success']} Enabled"
    )

    if amount is None:
        return status, "\u200b"

    amount_text = (
        f"{HOYOLAB_EMOJIS['original_resin']} "
        f"**{amount} Resin**"
    )

    return status, amount_text


class ResinAccountSelect(discord.ui.Select):

    def __init__(
        self,
        discord_user_id: int,
        options: list[discord.SelectOption],
        view: "ResinAccountView"
    ):
        super().__init__(
            placeholder="Select a Genshin Account...",
            options=options
        )

        self.discord_user_id = discord_user_id
        self.account_view = view

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer()

        genshin_uid = self.values[0]

        self.account_view.genshin_uid = genshin_uid

        accounts = await get_accounts(
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

            await interaction.edit_original_response(
                embed=embed,
                attachments=[],
                view=self.account_view
            )

            return

        embed, file = await _get_resin_message(
            self.discord_user_id,
            account
        )

        if file is not None:
            await interaction.edit_original_response(
                embed=embed,
                attachments=[file],
                view=self.account_view
            )
        else:
            await interaction.edit_original_response(
                embed=embed,
                attachments=[],
                view=self.account_view
            )


class AddManualResinReminderButton(
    discord.ui.Button
):

    def __init__(
        self,
        discord_user_id: int,
        view: "ResinAccountView"
    ):
        super().__init__(
            label="Add Manual Reminder",
            emoji=f"{MISC_EMOJIS['add']}",
            style=discord.ButtonStyle.secondary
        )

        self.discord_user_id = discord_user_id
        self.account_view = view

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                "This Resin panel belongs to someone else.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            ResinReminderModal(
                self.discord_user_id,
                self.account_view.genshin_uid,
                "manual",
                self.account_view,
                interaction.message
            )
        )


class AddAutomaticResinReminderButton(
    discord.ui.Button
):

    def __init__(
        self,
        discord_user_id: int,
        view: "ResinAccountView"
    ):
        super().__init__(
            label="Add Automatic Reminder",
            emoji=f"{MISC_EMOJIS['add']}",
            style=discord.ButtonStyle.secondary
        )

        self.discord_user_id = discord_user_id
        self.account_view = view

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                "This Resin panel belongs to someone else.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            ResinReminderModal(
                self.discord_user_id,
                self.account_view.genshin_uid,
                "automatic",
                self.account_view,
                interaction.message
            )
        )


class RemoveResinRemindersButton(
    discord.ui.Button
):

    def __init__(
        self,
        discord_user_id: int,
        view: "ResinAccountView"
    ):
        super().__init__(
            label="Remove Reminder(s)",
            emoji=f"{MISC_EMOJIS['remove']}",
            style=discord.ButtonStyle.secondary
        )

        self.discord_user_id = discord_user_id
        self.account_view = view

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                "This Resin panel belongs to someone else.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Remove Resin Reminders",
                description=(
                    "Which Resin reminders would you like to remove?"
                ),
                colour=discord.Colour.red()
            ),
            view=RemoveResinRemindersView(
                self.discord_user_id,
                self.account_view
            )
        )


class RemoveResinRemindersView(
    discord.ui.View
):

    def __init__(
        self,
        discord_user_id: int,
        resin_view: "ResinAccountView"
    ):
        super().__init__(
            timeout=300
        )

        self.discord_user_id = discord_user_id
        self.resin_view = resin_view

    async def remove(
        self,
        interaction: discord.Interaction,
        mode: str
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                "This Resin panel belongs to someone else.",
                ephemeral=True
            )

            return

        reminders = await get_reminders(
            self.discord_user_id
        )

        account_reminders = [
            reminder
            for reminder in reminders
            if reminder["genshin_uid"] == self.resin_view.genshin_uid
            and reminder["reminder_type"] == "resin"
            and reminder["reminder_mode"] in (
                ["manual", "automatic"]
                if mode == "both"
                else [mode]
            )
        ]

        if not account_reminders:
            await interaction.response.edit_message(
                embed=create_error_embed(
                    "No Reminders Found",
                    "There are no matching Resin reminders to remove.",
                    "not_found"
                ),
                view=self.resin_view
            )

            return

        for reminder in account_reminders:
            await delete_reminder(
                self.discord_user_id,
                reminder["id"]
            )

        accounts = await get_accounts(
            self.discord_user_id
        )

        account = next(
            (
                account
                for account in accounts
                if account["genshin_uid"]
                == self.resin_view.genshin_uid
            ),
            None
        )

        if account is None:
            await interaction.response.edit_message(
                embed=create_error_embed(
                    "Account Not Found",
                    "The selected Genshin account could not be found.",
                    "not_found"
                ),
                view=None
            )

            return

        embed, file = await _get_resin_message(
            self.discord_user_id,
            account
        )

        if file is not None:
            await interaction.response.edit_message(
                embed=embed,
                attachments=[file],
                view=ResinAccountView(
                    self.discord_user_id,
                    accounts,
                    self.resin_view.genshin_uid
                )
            )
        else:
            await interaction.response.edit_message(
                embed=embed,
                attachments=[],
                view=ResinAccountView(
                    self.discord_user_id,
                    accounts,
                    self.resin_view.genshin_uid
                )
            )

    @discord.ui.button(
        label="← Back",
        style=discord.ButtonStyle.primary
    )
    async def back(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):
        accounts = await get_accounts(
            self.discord_user_id
        )

        account = next(
            (
                account
                for account in accounts
                if account["genshin_uid"]
                   == self.resin_view.genshin_uid
            ),
            None
        )

        if account is None:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Account Not Found",
                    "The selected Genshin account could not be found.",
                    "not_found"
                ),
                ephemeral=True
            )

            return

        embed, file = await _get_resin_message(
            self.discord_user_id,
            account
        )

        if file is not None:
            await interaction.response.edit_message(
                embed=embed,
                attachments=[file],
                view=ResinAccountView(
                    self.discord_user_id,
                    accounts,
                    self.resin_view.genshin_uid
                )
            )
        else:
            await interaction.response.edit_message(
                embed=embed,
                attachments=[],
                view=ResinAccountView(
                    self.discord_user_id,
                    accounts,
                    self.resin_view.genshin_uid
                )
            )

    @discord.ui.button(
        label="Manual",
        style=discord.ButtonStyle.secondary
    )
    async def manual(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.remove(
            interaction,
            "manual"
        )

    @discord.ui.button(
        label="Automatic",
        style=discord.ButtonStyle.secondary
    )
    async def automatic(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.remove(
            interaction,
            "automatic"
        )

    @discord.ui.button(
        label="Both",
        style=discord.ButtonStyle.secondary
    )
    async def both(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.remove(
            interaction,
            "both"
        )


class ResinAccountView(discord.ui.View):

    def __init__(
        self,
        discord_user_id: int,
        accounts: list[dict],
        genshin_uid: str
    ):
        super().__init__(
            timeout=600
        )

        self.discord_user_id = discord_user_id
        self.genshin_uid = genshin_uid

        if len(accounts) > 1:
            self.add_item(
                ResinAccountSelect(
                    discord_user_id,
                    create_account_options(accounts),
                    self
                )
            )

        self.add_item(
            AddManualResinReminderButton(
                discord_user_id,
                self
            )
        )

        self.add_item(
            AddAutomaticResinReminderButton(
                discord_user_id,
                self
            )
        )

        self.add_item(
            RemoveResinRemindersButton(
                discord_user_id,
                self
            )
        )


class Resin(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):
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

        view = ResinAccountView(
            user_id,
            accounts,
            account["genshin_uid"]
        )

        embed, file = await _get_resin_message(
            user_id,
            account
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
        accounts = await get_accounts(
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

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        account = accounts[0]

        view = ResinAccountView(
            interaction.user.id,
            accounts,
            account["genshin_uid"]
        )

        embed, file = await _get_resin_message(
            interaction.user.id,
            account
        )

        await interaction.response.send_message(
            embed=embed,
            file=file,
            view=view,
            ephemeral=True
        )

    @commands.command(
        name="resin"
    )
    async def resin_prefix(
        self,
        ctx: commands.Context
    ):
        accounts = await get_accounts(
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Resin(bot))