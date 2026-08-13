import discord
from discord import app_commands
from discord.ext import commands
from utils.constants.emojis import HOYOLAB_EMOJIS, ERROR_EMOJIS
from utils.hoyolab.database import (
    get_accounts,
    get_reminders,
    delete_reminder,
    update_reminder,
)
from datetime import datetime, timezone
from utils.hoyolab.database import create_reminder
from utils.errors.error_handler import (
    create_error_embed,
    send_context_error,
)


REMINDER_NAMES = {
    "resin": "Resin",
    "expedition": "Expedition",
    "teapot": "Serenitea Pot",
    "transformer": "Parametric Transformer",
    "custom": "Custom",
}


REMINDER_EMOJIS = {
    "resin": HOYOLAB_EMOJIS["original_resin"],
    "expedition": HOYOLAB_EMOJIS["expeditions"],
    "teapot": HOYOLAB_EMOJIS["serenitea_pot"],
    "transformer": HOYOLAB_EMOJIS["parametric_transformer"],
    "custom": HOYOLAB_EMOJIS["custom"],
}


def get_reminder_name(reminder_type: str) -> str:
    return REMINDER_NAMES.get(
        reminder_type,
        reminder_type.replace("_", " ").title()
    )


def get_reminder_emoji(reminder_type: str) -> str:
    return REMINDER_EMOJIS.get(
        reminder_type,
        f"{HOYOLAB_EMOJIS['notification']}"
    )

def get_account_name(account: dict) -> str:
    return (
        account.get("cyrene_nickname")
        or account.get("nickname")
        or f"UID {account['genshin_uid']}"
    )


def format_account_info(account: dict) -> str:
    name = get_account_name(account)

    return (
        f"**Name**: {name}\n"
        f"**UID**: {account['genshin_uid']}\n"
        f"**AR**: {account['level'] or 'Unknown'}"
    )


def format_reminder(reminder: dict) -> str:
    reminder_type = reminder["reminder_type"]

    emoji = get_reminder_emoji(
        reminder_type
    )

    name = get_reminder_name(
        reminder_type
    )

    status = (
        "Enabled"
        if reminder["enabled"]
        else "Disabled"
    )

    config = reminder.get("config") or {}

    details = []

    if reminder_type == "resin":
        amount = config.get("amount")

        if amount is not None:
            details.append(
                f"at **{amount} Resin**"
            )

    elif reminder_type == "custom":
        message = config.get("message")

        if message:
            details.append(
                f'"{message}"'
            )

    detail_text = ""

    if details:
        detail_text = " • " + " • ".join(details)

    return (
        f"{emoji} **{name}**\n"
        f"└ {status}{detail_text}"
    )


def build_reminders_embed(
    account: dict,
    reminders: list[dict]
) -> discord.Embed:

    embed = discord.Embed(
        title="Reminders",
        description=(
            "Manage your reminders for the selected account."
        ) + "\n\u200b",
        colour=discord.Colour.gold()
    )

    embed.add_field(
        name="Account",
        value=format_account_info(account) + "\n\u200b",
        inline=False
    )

    sections = [
        ("resin", "Resin"),
        ("expedition", "Expeditions"),
        ("teapot", "Serenitea Pot"),
        ("transformer", "Parametric Transformer"),
        ("custom", "Custom"),
    ]

    for reminder_type, name in sections:
        emoji = get_reminder_emoji(reminder_type)

        manual = next(
            (
                reminder
                for reminder in reminders
                if reminder["reminder_type"] == reminder_type
                   and reminder["reminder_mode"] == "manual"
            ),
            None
        )

        automatic = next(
            (
                reminder
                for reminder in reminders
                if reminder["reminder_type"] == reminder_type
                   and reminder["reminder_mode"] == "automatic"
            ),
            None
        )

        def get_reminder_display(
                reminder: dict | None
        ) -> tuple[str, str]:

            if (
                    reminder is None
                    or not reminder["enabled"]
            ):
                return (
                    f"{ERROR_EMOJIS['error']} Disabled",
                    ""
                )

            config = reminder.get("config") or {}

            status = (
                f"{ERROR_EMOJIS['success']} Enabled"
            )

            details = ""

            if reminder_type == "resin":
                amount = config.get("amount")

                if amount is not None:
                    details = (
                        f"{HOYOLAB_EMOJIS['original_resin']} "
                        f"**{amount} Resin**"
                    )

            elif reminder_type == "custom":
                message = config.get("message")

                if message:
                    details = f'"{message}"'

            return status, details

        manual_status, manual_details = (
            get_reminder_display(manual)
        )

        automatic_status, automatic_details = (
            get_reminder_display(automatic)
        )

        embed.add_field(
            name=f"{emoji} {name}",
            value=(
                "⦁\u2002**Manual Reminder**\n"
                "⦁\u2002**Automatic Reminder**"
            ) + "\n\u200b",
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
                f"{manual_details or '\u200b'}\n"
                f"{automatic_details or '\u200b'}"
            ),
            inline=True
        )

    return embed


class ReminderSelect(discord.ui.Select):

    def __init__(
        self,
        reminders: list[dict],
        view: "RemindersView"
    ):
        options = []

        for reminder in reminders:
            reminder_type = reminder["reminder_type"]

            emoji = get_reminder_emoji(
                reminder_type
            )

            name = get_reminder_name(
                reminder_type
            )

            config = reminder.get("config") or {}

            description = name

            if reminder_type == "resin":
                amount = config.get("amount")

                if amount is not None:
                    description = (
                        f"Resin at {amount}"
                    )

            options.append(
                discord.SelectOption(
                    label=name[:100],
                    description=description[:100],
                    emoji=emoji,
                    value=str(reminder["id"])
                )
            )

        super().__init__(
            placeholder="Select a reminder...",
            options=options
        )

        self.reminders = reminders
        self.view_reference = view

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        reminder_id = int(
            self.values[0]
        )

        reminder = next(
            (
                reminder
                for reminder in self.reminders
                if reminder["id"] == reminder_id
            ),
            None
        )

        if reminder is None:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Reminder Not Found",
                    "That reminder no longer exists.",
                    "not_found"
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            embed=build_reminder_detail_embed(
                reminder
            ),
            view=ReminderManagementView(
                interaction.user.id,
                reminder
            ),
            ephemeral=True
        )


def build_reminder_detail_embed(
    reminder: dict
) -> discord.Embed:

    reminder_type = reminder["reminder_type"]

    emoji = get_reminder_emoji(
        reminder_type
    )

    name = get_reminder_name(
        reminder_type
    )

    config = reminder.get("config") or {}

    embed = discord.Embed(
        title=f"{emoji} {name} Reminder",
        colour=discord.Colour.blurple()
    )

    embed.add_field(
        name="Status",
        value=(
            "Enabled"
            if reminder["enabled"]
            else "Disabled"
        ),
        inline=True
    )

    embed.add_field(
        name="Delivery",
        value=reminder["delivery_type"].upper(),
        inline=True
    )

    if reminder["genshin_uid"]:
        embed.add_field(
            name="Genshin UID",
            value=reminder["genshin_uid"],
            inline=False
        )

    if config:
        config_lines = []

        for key, value in config.items():
            config_lines.append(
                f"**{key.replace('_', ' ').title()}:** {value}"
            )

        embed.add_field(
            name="Configuration",
            value="\n".join(config_lines),
            inline=False
        )

    if reminder["next_trigger_at"]:
        timestamp = int(
            reminder["next_trigger_at"].timestamp()
        )

        embed.add_field(
            name="Next Trigger",
            value=f"<t:{timestamp}:R>",
            inline=False
        )

    return embed


class ReminderManagementView(
    discord.ui.View
):

    def __init__(
        self,
        discord_user_id: int,
        reminder: dict
    ):
        super().__init__(
            timeout=300
        )

        self.discord_user_id = discord_user_id
        self.reminder = reminder

    @discord.ui.button(
        label="Enable",
        style=discord.ButtonStyle.success
    )
    async def enable(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Permission Denied",
                    "This reminder belongs to someone else.",
                    "permission"
                ),
                ephemeral=True
            )

            return

        await update_reminder(
            self.discord_user_id,
            self.reminder["id"],
            enabled=True
        )

        self.reminder["enabled"] = True

        await interaction.response.edit_message(
            embed=build_reminder_detail_embed(
                self.reminder
            ),
            view=self
        )

    @discord.ui.button(
        label="Disable",
        style=discord.ButtonStyle.secondary
    )
    async def disable(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Permission Denied",
                    "This reminder belongs to someone else.",
                    "permission"
                ),
                ephemeral=True
            )

            return

        await update_reminder(
            self.discord_user_id,
            self.reminder["id"],
            enabled=False
        )

        self.reminder["enabled"] = False

        await interaction.response.edit_message(
            embed=build_reminder_detail_embed(
                self.reminder
            ),
            view=self
        )

    @discord.ui.button(
        label="Delete",
        style=discord.ButtonStyle.danger
    )
    async def delete(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Permission Denied",
                    "This reminder belongs to someone else.",
                    "permission"
                ),
                ephemeral=True
            )

            return

        deleted = await delete_reminder(
            self.discord_user_id,
            self.reminder["id"]
        )

        if not deleted:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Reminder Not Found",
                    "That reminder no longer exists.",
                    "not_found"
                ),
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            content="Reminder deleted.",
            embed=None,
            view=None
        )


class ReminderAccountSelect(discord.ui.Select):

    def __init__(
        self,
        accounts: list[dict],
        discord_user_id: int
    ):
        self.accounts = accounts
        self.discord_user_id = discord_user_id

        options = []

        for account in accounts:
            name = get_account_name(account)

            options.append(
                discord.SelectOption(
                    label=name[:100],
                    description=(
                        f"UID: {account['genshin_uid']} "
                        f"• AR {account['level'] or 'Unknown'}"
                    )[:100],
                    value=account["genshin_uid"]
                )
            )

        super().__init__(
            placeholder="Select an account...",
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Permission Denied",
                    "This reminder belongs to someone else.",
                    "permission"
                ),
                ephemeral=True
            )

            return

        selected_uid = self.values[0]

        account = next(
            (
                account
                for account in self.accounts
                if account["genshin_uid"] == selected_uid
            ),
            None
        )

        if account is None:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Account Not Found",
                    "That account could not be found.",
                    "not_found"
                ),
                ephemeral=True
            )

            return

        reminders = await get_reminders(
            interaction.user.id
        )

        account_reminders = [
            reminder
            for reminder in reminders
            if reminder["genshin_uid"] == selected_uid
        ]

        embed = build_reminders_embed(
            account,
            account_reminders
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RemindersView(
                interaction.user.id,
                self.accounts,
                account
            )
        )

class ResinReminderButton(discord.ui.Button):

    def __init__(
        self,
        discord_user_id: int,
        genshin_uid: str,
        mode: str,
        reminders_view: "RemindersView"
    ):
        self.discord_user_id = discord_user_id
        self.genshin_uid = genshin_uid
        self.mode = mode
        self.reminders_view = reminders_view

        super().__init__(
            label=(
                "Manual Resin"
                if mode == "manual"
                else "Automatic Resin"
            ),
            emoji=HOYOLAB_EMOJIS["original_resin"],
            style=(
                discord.ButtonStyle.primary
                if mode == "manual"
                else discord.ButtonStyle.secondary
            )
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Permission Denied",
                    "This reminder belongs to someone else.",
                    "permission"
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            ResinReminderModal(
                self.discord_user_id,
                self.genshin_uid,
                self.mode,
                self.reminders_view,
                interaction.message
            )
        )


class RemindersView(discord.ui.View):

    def __init__(
        self,
        discord_user_id: int,
        accounts: list[dict],
        selected_account: dict
    ):
        super().__init__(
            timeout=600
        )

        self.discord_user_id = discord_user_id
        self.accounts = accounts
        self.selected_account = selected_account

        self.add_item(
            ReminderAccountSelect(
                accounts,
                discord_user_id
            )
        )

        self.add_item(
            ResinReminderButton(
                discord_user_id,
                selected_account["genshin_uid"],
                "manual",
                self
            )
        )

        self.add_item(
            ResinReminderButton(
                discord_user_id,
                selected_account["genshin_uid"],
                "automatic",
                self
            )
        )


class ManualReminderButton(
    discord.ui.Button
):

    def __init__(
        self,
        discord_user_id: int
    ):
        super().__init__(
            label="Set Manual Reminder",
            emoji=HOYOLAB_EMOJIS["notification"],
            style=discord.ButtonStyle.primary
        )

        self.discord_user_id = discord_user_id

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if interaction.user.id != self.discord_user_id:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Permission Denied",
                    "This reminder belongs to someone else.",
                    "permission"
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            ManualReminderModal(
                self.discord_user_id
            )
        )


class Reminders(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot

    @app_commands.command(
        name="reminders",
        description="Manage your reminders."
    )
    async def reminders(
            self,
            interaction: discord.Interaction
    ):
        accounts = await get_accounts(
            interaction.user.id
        )

        if not accounts:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "No Accounts Linked",
                    "You don't have any HoYoLAB accounts linked.",
                    "not_found"
                ),
                ephemeral=True
            )

            return

        selected_account = accounts[0]

        reminders = await get_reminders(
            interaction.user.id
        )

        account_reminders = [
            reminder
            for reminder in reminders
            if reminder["genshin_uid"]
               == selected_account["genshin_uid"]
        ]

        embed = build_reminders_embed(
            selected_account,
            account_reminders
        )

        view = RemindersView(
            interaction.user.id,
            accounts,
            selected_account
        )

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

    @commands.command(
        name="reminders"
    )
    async def reminders_prefix(
            self,
            ctx: commands.Context
    ):
        accounts = await get_accounts(
            ctx.author.id
        )

        if not accounts:
            await send_context_error(
                ctx,
                "No Accounts Linked",
                "You don't have any HoYoLAB accounts linked.",
                "not_found"
            )

            return

        selected_account = accounts[0]

        reminders = await get_reminders(
            ctx.author.id
        )

        account_reminders = [
            reminder
            for reminder in reminders
            if reminder["genshin_uid"]
               == selected_account["genshin_uid"]
        ]

        embed = build_reminders_embed(
            selected_account,
            account_reminders
        )

        view = RemindersView(
            ctx.author.id,
            accounts,
            selected_account
        )

        await ctx.send(
            embed=embed,
            view=view
        )

class ResinReminderModal(discord.ui.Modal):

    def __init__(
        self,
        discord_user_id: int,
        genshin_uid: str,
        mode: str,
        reminders_view: "RemindersView",
        parent_message: discord.Message
    ):
        super().__init__(
            title=(
                "Set Manual Resin Reminder"
                if mode == "manual"
                else "Set Automatic Resin Reminder"
            )
        )

        self.discord_user_id = discord_user_id
        self.genshin_uid = genshin_uid
        self.mode = mode
        self.reminders_view = reminders_view
        self.parent_message = parent_message

        self.amount = discord.ui.TextInput(
            label="Resin Amount",
            placeholder="Enter an amount from 1 to 200",
            min_length=1,
            max_length=3,
            required=True
        )

        self.add_item(self.amount)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        try:
            amount = int(self.amount.value)

        except ValueError:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Invalid Resin Amount",
                    "Please enter a valid Resin amount.",
                    "invalid_input"
                ),
                ephemeral=True
            )

            return

        if not 1 <= amount <= 200:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Invalid Resin Amount",
                    "Resin must be between **1 and 200**.",
                    "invalid_input"
                ),
                ephemeral=True
            )

            return

        await create_reminder(
            discord_user_id=self.discord_user_id,
            reminder_type="resin",
            genshin_uid=self.genshin_uid,
            config={
                "amount": amount
            },
            delivery_type="dm",
            reminder_mode=self.mode,
            next_trigger_at=datetime.now(timezone.utc)
        )

        reminders = await get_reminders(
            self.discord_user_id
        )

        account_reminders = [
            reminder
            for reminder in reminders
            if reminder["genshin_uid"] == self.genshin_uid
        ]

        account = next(
            (
                account
                for account in self.reminders_view.accounts
                if account["genshin_uid"] == self.genshin_uid
            ),
            None
        )

        if account is not None:
            embed = build_reminders_embed(
                account,
                account_reminders
            )

            try:
                await self.parent_message.edit(
                    embed=embed,
                    view=RemindersView(
                        self.discord_user_id,
                        self.reminders_view.accounts,
                        account
                    )
                )

            except discord.NotFound:
                pass

        confirmation = create_error_embed(
            "Resin Reminder Set",
            (
                f"Your **{self.mode.title()} Resin Reminder** has been set to **{amount} Resin**."
            ),
            "success"
        )

        await interaction.response.send_message(
            embed=confirmation,
            ephemeral=True
        )


class ManualReminderModal(discord.ui.Modal):
    def __init__(
        self,
        discord_user_id: int
    ):
        super().__init__(
            title="Set Manual Reminder"
        )

        self.discord_user_id = discord_user_id

        self.message = discord.ui.TextInput(
            label="Reminder",
            placeholder="What should I remind you about?",
            max_length=500,
            required=True
        )

        self.date = discord.ui.TextInput(
            label="Date",
            placeholder="DD/MM/YYYY",
            max_length=10,
            required=True
        )

        self.time = discord.ui.TextInput(
            label="Time",
            placeholder="HH:MM (24-hour)",
            max_length=5,
            required=True
        )

        self.add_item(self.message)
        self.add_item(self.date)
        self.add_item(self.time)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        try:
            naive_datetime = datetime.strptime(
                f"{self.date.value} {self.time.value}",
                "%d/%m/%Y %H:%M"
            )

        except ValueError:
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Invalid Date or Time",
                    (
                        "Please enter a valid date and time.\n\n"
                        "Example: `12/08/2026` and `18:30`."
                    ),
                    "invalid_input"
                ),
                ephemeral=True
            )

            return

        trigger_at = naive_datetime.astimezone(
            timezone.utc
        )

        if trigger_at <= datetime.now(timezone.utc):
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Invalid Reminder Time",
                    "The reminder time must be in the future.",
                    "invalid_input"
                ),
                ephemeral=True
            )

            return

        await create_reminder(
            discord_user_id=self.discord_user_id,
            reminder_type="custom",
            config={
                "message": self.message.value
            },
            delivery_type="dm",
            reminder_mode="manual",
            next_trigger_at=trigger_at
        )

        embed = create_error_embed(
            "Reminder Set",
            (
                f"I'll remind you "
                f"<t:{int(trigger_at.timestamp())}:R>."
            ),
            "success"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )



async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))