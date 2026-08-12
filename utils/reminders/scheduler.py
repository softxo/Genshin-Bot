import asyncio
import logging
import traceback
import discord
from datetime import datetime, timezone, timedelta
from utils.hoyolab.account_client import get_account_client
from utils.hoyolab.database import (
    get_due_reminders,
    update_reminder,
)
from utils.hoyolab.daily_note import get_resin


logger = logging.getLogger(__name__)


CHECK_INTERVAL = 10
RESIN_REGEN_SECONDS = 480


class ReminderScheduler:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.task: asyncio.Task | None = None
        self.running = False

    def is_running(self) -> bool:
        return (
            self.running
            and self.task is not None
            and not self.task.done()
        )

    def start(self):
        if self.task is not None and not self.task.done():
            return

        self.running = True

        self.task = asyncio.create_task(
            self._run(),
            name="reminder_scheduler"
        )

        logger.info("Reminder scheduler started.")

    async def stop(self):
        self.running = False

        if self.task is not None:
            self.task.cancel()

            try:
                await self.task
            except asyncio.CancelledError:
                pass

            self.task = None

        logger.info("Reminder scheduler stopped.")

    async def _run(self):
        print("[ReminderScheduler] Loop started.")

        while self.running:
            try:
                print("[ReminderScheduler] Checking reminders...")

                await self.process_due_reminders()

            except asyncio.CancelledError:
                raise

            except Exception as error:
                logger.exception(
                    "[ReminderScheduler] ERROR: %r",
                    error
                )

            await asyncio.sleep(CHECK_INTERVAL)

    async def process_due_reminders(self):
        reminders = await get_due_reminders()

        print(
            f"[ReminderScheduler] Due reminders: {len(reminders)}"
        )

        if not reminders:
            return

        for reminder in reminders:
            print(
                "[ReminderScheduler] Processing reminder:",
                reminder["id"],
                reminder["reminder_type"],
                reminder.get("reminder_mode"),
                reminder.get("genshin_uid"),
                reminder.get("next_trigger_at")
            )

            try:
                completed = await self.process_reminder(
                    reminder
                )

                if completed:
                    print(
                        "[ReminderScheduler] Reminder completed:",
                        reminder["id"]
                    )
                else:
                    print(
                        "[ReminderScheduler] Reminder rescheduled:",
                        reminder["id"]
                    )

            except Exception as error:
                print(
                    "[ReminderScheduler] REMINDER ERROR:",
                    reminder["id"],
                    repr(error)
                )

                traceback.print_exc()

    async def process_reminder(
            self,
            reminder: dict
    ) -> bool:
        if reminder["reminder_mode"] == "manual":
            return await self.handle_manual(reminder)

        reminder_type = reminder["reminder_type"]

        handler = {
            "resin": self.handle_resin,
            "expedition": self.handle_expedition,
            "teapot": self.handle_teapot,
            "transformer": self.handle_transformer,
            "custom": self.handle_custom,
        }.get(reminder_type)

        if handler is None:
            logger.warning(
                "Unknown reminder type '%s' for reminder %s.",
                reminder_type,
                reminder["id"]
            )
            return False

        return await handler(reminder)

    async def handle_manual(
        self,
        reminder: dict
    ):
        config = reminder.get("config") or {}

        message = config.get(
            "message",
            "Your reminder is due."
        )

        sent = await self.send_reminder(
            reminder,
            title="Reminder",
            message=message
        )

        if not sent:
            return False

        await update_reminder(
            reminder["discord_user_id"],
            reminder["id"],
            enabled=False,
            last_triggered_at=datetime.now(timezone.utc),
            next_trigger_at=None
        )

        return True

    async def handle_resin(
            self,
            reminder: dict
    ):
        reminder_id = reminder["id"]
        user_id = reminder["discord_user_id"]
        genshin_uid = reminder.get("genshin_uid")

        print(
            f"[ReminderScheduler] RESIN HANDLER STARTED: "
            f"id={reminder_id}, user={user_id}, uid={genshin_uid}"
        )

        if not genshin_uid:
            print(
                f"[ReminderScheduler] Resin reminder {reminder_id} "
                f"has no Genshin UID."
            )

            await update_reminder(
                user_id,
                reminder_id,
                enabled=False,
                next_trigger_at=None
            )

            return True

        config = reminder.get("config") or {}
        amount = config.get("amount")

        print(
            f"[ReminderScheduler] Reminder {reminder_id} config: "
            f"{config}"
        )

        if amount is None:
            print(
                f"[ReminderScheduler] Resin reminder {reminder_id} "
                f"has no target amount."
            )

            await update_reminder(
                user_id,
                reminder_id,
                enabled=False,
                next_trigger_at=None
            )

            return True

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            print(
                f"[ReminderScheduler] Invalid Resin target "
                f"for reminder {reminder_id}: {amount!r}"
            )

            await update_reminder(
                user_id,
                reminder_id,
                enabled=False,
                next_trigger_at=None
            )

            return True

        print(
            f"[ReminderScheduler] Resin target for reminder "
            f"{reminder_id}: {amount}"
        )

        print(
            f"[ReminderScheduler] Getting account client "
            f"for user={user_id}, uid={genshin_uid}..."
        )

        try:
            client = await get_account_client(
                user_id,
                genshin_uid
            )
        except Exception:
            logger.exception(
                "Failed to get account client for Resin reminder %s.",
                reminder_id
            )

            await self.retry_reminder(
                reminder,
                seconds=60
            )

            return False

        print(
            f"[ReminderScheduler] Account client result: {client!r}"
        )

        if client is None:
            print(
                f"[ReminderScheduler] No account client found "
                f"for reminder {reminder_id}."
            )

            await self.retry_reminder(
                reminder,
                seconds=60
            )

            return

        try:
            async with client:
                print(
                    f"[ReminderScheduler] Fetching daily note "
                    f"for reminder {reminder_id}..."
                )

                response = await client.get_genshin_daily_note(
                    client.genshin_uid,
                    client.genshin_server
                )

                print(
                    f"[ReminderScheduler] Daily note received "
                    f"for reminder {reminder_id}."
                )

        except Exception:
            logger.exception(
                "Failed to fetch Resin for reminder %s.",
                reminder_id
            )

            await self.retry_reminder(
                reminder,
                seconds=60
            )

            return

        try:
            current_resin, max_resin, recovery = get_resin(
                response
            )
        except Exception:
            logger.exception(
                "Failed to parse Resin response for reminder %s.",
                reminder_id
            )

            await self.retry_reminder(
                reminder,
                seconds=60
            )

            return

        print(
            f"[ReminderScheduler] Resin status: "
            f"{current_resin}/{max_resin}, "
            f"target={amount}, "
            f"recovery={recovery}s"
        )

        if current_resin >= amount:
            print(
                f"[ReminderScheduler] TARGET REACHED: "
                f"{current_resin} >= {amount}"
            )

            sent = await self.send_reminder(
                reminder,
                title="Resin Reminder",
                message=(
                    f"Your Resin has reached "
                    f"**{current_resin}/{max_resin}** "
                    f"(target: **{amount}**)."
                )
            )

            print(
                f"[ReminderScheduler] DM result for reminder "
                f"{reminder_id}: {sent}"
            )

            if sent:
                await update_reminder(
                    user_id,
                    reminder_id,
                    enabled=False,
                    next_trigger_at=None,
                    last_triggered_at=datetime.now(timezone.utc)
                )

                print(
                    f"[ReminderScheduler] Reminder {reminder_id} "
                    f"completed and disabled."
                )

                return True

            else:
                print(
                    f"[ReminderScheduler] DM failed. "
                    f"Retrying reminder {reminder_id} in 60 seconds."
                )

                await self.retry_reminder(
                    reminder,
                    seconds=60
                )

                return False


        resin_needed = amount - current_resin

        print(
            f"[ReminderScheduler] Target not reached. "
            f"{resin_needed} Resin needed."
        )

        await self.schedule_resin_reminder(
            reminder,
            current_resin,
            amount,
            recovery
        )

        return False


    async def schedule_resin_reminder(
        self,
        reminder: dict,
        current_resin: int,
        target_resin: int,
        recovery: int
    ):
        resin_needed = target_resin - current_resin

        if resin_needed <= 0:
            return

        seconds_until_target = (
            recovery
            + ((resin_needed - 1) * RESIN_REGEN_SECONDS)
        )

        next_trigger_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=seconds_until_target)
        )

        logger.info(
            "Resin reminder %s scheduled for %s "
            "(current=%s target=%s).",
            reminder["id"],
            next_trigger_at,
            current_resin,
            target_resin
        )

        await update_reminder(
            reminder["discord_user_id"],
            reminder["id"],
            next_trigger_at=next_trigger_at
        )

    async def retry_reminder(
        self,
        reminder: dict,
        seconds: int
    ):
        next_trigger_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=seconds)
        )

        await update_reminder(
            reminder["discord_user_id"],
            reminder["id"],
            next_trigger_at=next_trigger_at
        )

    async def handle_expedition(
        self,
        reminder: dict
    ):
        logger.debug(
            "Expedition reminder %s is not implemented yet.",
            reminder["id"]
        )

        return False

    async def handle_teapot(
        self,
        reminder: dict
    ):
        logger.debug(
            "Teapot reminder %s is not implemented yet.",
            reminder["id"]
        )

        return False

    async def handle_transformer(
        self,
        reminder: dict
    ):
        logger.debug(
            "Transformer reminder %s is not implemented yet.",
            reminder["id"]
        )

        return False

    async def handle_custom(
            self,
            reminder: dict
    ) -> bool:
        config = reminder.get("config") or {}

        message = config.get("message")

        if not message:
            logger.warning(
                "Custom reminder %s has no message.",
                reminder["id"]
            )

            await update_reminder(
                reminder["discord_user_id"],
                reminder["id"],
                enabled=False,
                next_trigger_at=None
            )

            return True

        sent = await self.send_reminder(
            reminder,
            title="Reminder",
            message=message
        )

        if not sent:
            return False

        await update_reminder(
            reminder["discord_user_id"],
            reminder["id"],
            enabled=False,
            last_triggered_at=datetime.now(timezone.utc),
            next_trigger_at=None
        )

        return True

    async def send_reminder(
            self,
            reminder: dict,
            *,
            title: str,
            message: str
    ) -> bool:
        user_id = reminder["discord_user_id"]

        print(
            f"[ReminderScheduler] Attempting to send DM "
            f"to {user_id}..."
        )

        user = self.bot.get_user(user_id)

        if user is None:
            print(
                f"[ReminderScheduler] User {user_id} isn't cached. "
                f"Fetching..."
            )

            try:
                user = await self.bot.fetch_user(user_id)

            except discord.NotFound:
                print(
                    f"[ReminderScheduler] Discord user {user_id} "
                    f"does not exist."
                )
                return False

            except discord.HTTPException as error:
                print(
                    f"[ReminderScheduler] Failed to fetch user "
                    f"{user_id}: {error!r}"
                )
                return False

        print(
            f"[ReminderScheduler] User resolved: "
            f"{user} ({user.id})"
        )

        embed = discord.Embed(
            title=title,
            description=message,
            colour=discord.Colour.blurple()
        )

        delivery_type = reminder.get(
            "delivery_type",
            "dm"
        )

        if delivery_type != "dm":
            print(
                f"[ReminderScheduler] Unsupported delivery type: "
                f"{delivery_type!r}"
            )
            return False

        try:
            await user.send(embed=embed)

        except discord.Forbidden as error:
            print(
                f"[ReminderScheduler] Discord FORBIDDEN while "
                f"sending DM to {user.id}: {error!r}"
            )
            return False

        except discord.HTTPException as error:
            print(
                f"[ReminderScheduler] Discord HTTP error while "
                f"sending DM to {user.id}: {error!r}"
            )
            return False

        print(
            f"[ReminderScheduler] *** DM SENT SUCCESSFULLY *** "
            f"to {user.id}"
        )

        return True