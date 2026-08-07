import uuid
import discord
from discord.ext import commands
from discord import app_commands
from utils.constants.emojis import ERROR_EMOJIS, ERROR_TYPE_EMOJIS
from utils.constants.colours import ERROR_COLOURS, ERROR_TYPE_COLOURS
from utils.errors.error_logger import log_error


def create_error_embed(
        title: str,
        description: str,
        error_type: str,
) -> discord.Embed:

    emoji = ERROR_TYPE_EMOJIS.get(
        error_type,
        ERROR_EMOJIS["error"]
    )

    colour = discord.Colour(
        ERROR_TYPE_COLOURS.get(
            error_type,
            ERROR_COLOURS["error"]
        )
    )

    embed = discord.Embed(
        title=f"{emoji} {title}",
        description=description,
        colour=colour
    )

    return embed


async def send_interaction_error(
        interaction: discord.Interaction,
        title: str,
        description: str,
        error_type: str,
        *,
        ephemeral: bool = True
):
    embed = create_error_embed(
        title,
        description,
        error_type
    )

    if interaction.response.is_done():
        await interaction.followup.send(
            embed=embed,
            ephemeral=ephemeral
        )
    else:
        await interaction.response.send_message(
            embed=embed,
            ephemeral=ephemeral
        )


async def send_context_error(
        ctx: commands.Context,
        title: str,
        description: str,
        error_type: str
):
    embed = create_error_embed(
        title,
        description,
        error_type
    )

    await ctx.send(embed=embed)

async def send_missing_argument(
        ctx: commands.Context,
        usage: str,
        argument: str | None = None
):
    if argument:
        description = (
            f"You're missing the required argument `{argument}`.\n\n"
            f"**Usage:** `{usage}`"
        )
    else:
        description = (
            "You're missing one or more required arguments.\n\n"
            f"**Usage:** `{usage}`"
        )

    await send_context_error(
        ctx,
        "Missing Argument",
        description,
        "missing_argument"
    )

async def send_invalid_input(
    ctx: commands.Context,
    description: str,
):
    await send_context_error(
        ctx,
        "Invalid Input",
        description,
        "invalid_input",
    )


async def send_not_found(
    ctx: commands.Context,
    description: str,
):
    await send_context_error(
        ctx,
        "Not Found",
        description,
        "not_found",
    )


async def send_permission_error(
    ctx: commands.Context,
    description: str,
):
    await send_context_error(
        ctx,
        "Permission Denied",
        description,
        "permission",
    )


async def send_bot_permission_error(
    ctx: commands.Context,
    description: str,
):
    await send_context_error(
        ctx,
        "Missing Bot Permissions",
        description,
        "bot_permission",
    )


def generate_error_id() -> str:
    return uuid.uuid4().hex[:6].upper()


async def handle_app_command_error(
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.CommandInvokeError):
        original = error.original
    else:
        original = error

# PERM ERROR

    if isinstance(error, app_commands.MissingPermissions):
        permissions = ", ".join(
            permission.replace("_", " ").title()
            for permission in error.missing_permissions
        )

        await send_interaction_error(
            interaction,
            "Permission Denied",
            (
                "You do not have the required permissions to use this command.\n\n"
                f"**Required:** {permissions}"
            ),
            "permission"
        )
        return

    if isinstance(error, app_commands.BotMissingPermissions):
        permissions = ", ".join(
            permission.replace("_", " ").title()
            for permission in error.missing_permissions
        )

        await send_interaction_error(
            interaction,
            "Missing BOT Permissions",
            (
                "I don't have the permissions required to execute this command.\n\n"
                f"**Required:** {permissions}"
            ),
            "bot_permission"
        )
        return

# CDs

    if isinstance(error, app_commands.CommandOnCooldown):
        await send_interaction_error(
            interaction,
            "Slow Down",
            (
                "You're using this command too quickly.\n\n"
                f"Please try again in **{error.retry_after:.1f} seconds**."
            ),
            "cooldown"
        )
        return

# CHECKS

    if isinstance(error, app_commands.CheckFailure):
        await send_interaction_error(
            interaction,
            "Command Unavailable",
            "You are not currently allowed to use this command.",
            "error"
        )
        return

# TRANSFORMER / ARGUMENT ERRORS

    if isinstance(error, app_commands.TransformerError):
        await send_interaction_error(
            interaction,
            "Invalid Input",
            (
                "One of the values you provided is invalid.\n\n"
                "Please check your input and try again."
            ),
            "invalid_input"
        )
        return

# DISCORD ERRORS

    if isinstance(original, discord.Forbidden):
        await send_interaction_error(
            interaction,
            "Permission Error",
            (
                "Discord prevented me from completing this action because I don't have the required permissions."
            ),
            "permission"
        )
        return

    if isinstance(original, discord.NotFound):
        await send_interaction_error(
            interaction,
            "Not Found",
            (
                "The requested Discord resource could not be found."
            ),
            "not_found"
        )
        return

    if isinstance(original, discord.HTTPException):
        await send_interaction_error(
            interaction,
            "Discord Error",
            (
                "Discord encountered a problem while processing this request.\n\n"
                "Please try again in a moment."
            ),
            "error"
        )
        return

# UNKNOWN / INTERNAL ERRORS

    error_id = generate_error_id()

    log_error(
        original,
        error_id,
        command=interaction.command.qualified_name
        if interaction.command
        else None,
        user_id=interaction.user.id,
        guild_id=interaction.guild.id
        if interaction.guild
        else None,
        channel_id=interaction.channel.id
        if interaction.channel
        else None
    )

    await send_interaction_error(
        interaction,
        "Unexpected Error",
        (
            "Something went wrong while executing the command.\n\n"
            "Please try again later.\n\n"
            f"**Error ID:** `{error_id}`"
        ),
        "unexpected"
    )


async def handle_prefix_command_error(
        ctx: commands.Context,
        error: commands.CommandError
):
    if getattr(error, "handled", False):
        return

    if isinstance(error, commands.CommandInvokeError):
        original = error.original
    else:
        original = error

# MISSING ARG

    if isinstance(error, commands.MissingRequiredArgument):
        await send_context_error(
            ctx,
            "Missing Argument",
            (
                f"You're missing the required argument `{error.param.name}`.\n\n"
                f"**Usage:** `{ctx.prefix}{ctx.command.qualified_name} "
                f"{' '.join(f'<{p.name}>' for p in ctx.command.clean_params.values())}`"
            ),
            "missing_argument"
        )
        return

# BAD ARG

    if isinstance(error, commands.BadArgument):
        await send_context_error(
            ctx,
            "Invalid Input",
            (
                "One or more of the values you provided could not be understood.\n\n"
                "Please check your arguments and try again."
            ),
            "invalid_input"
        )
        return

# MISSING USER PERM

    if isinstance(error, commands.MissingPermissions):
        permissions = ", ".join(
            permission.replace("_", " ").title()
            for permission in error.missing_permissions
        )

        await send_context_error(
            ctx,
            "Permission Denied",
            (
                "You do not have the required permissions to use this command.\n\n"
                f"**Required:** {permissions}"
            ),
            "permission"
        )
        return

# MISSING BOT PERM

    if isinstance(error, commands.BotMissingPermissions):
        permissions = ", ".join(
            permission.replace("_", " ").title()
            for permission in error.missing_permissions
        )

        await send_context_error(
            ctx,
            "Missing Bot Permissions",
            (
                "I don't have the permissions required to execute this command.\n\n"
                f"**Required:** {permissions}"
            ),
            "bot_permission"
        )
        return

# COOLDOWN

    if isinstance(error, commands.CommandOnCooldown):
        await send_context_error(
            ctx,
            "Slow Down",
            (
                "You're using this command too quickly.\n\n"
                f"Please try again in **{error.retry_after:.1f} seconds**."
            ),
            "cooldown"
        )
        return

# CHECKS

    if isinstance(error, commands.CheckFailure):
        await send_context_error(
            ctx,
            "Command Unavailable",
            "You are not currently allowed to use this command.",
            "error"
        )
        return

# DISCORD ERRORS

    if isinstance(original, discord.NotFound):
        await send_context_error(
            ctx,
            "Not Found",
            "The requested Discord resource could not be found.",
            "not_found"
        )
        return

    if isinstance(original, discord.Forbidden):
        await send_context_error(
            ctx,
            "Permission Error",
            (
                "Discord prevented me from completing this action "
                "because I don't have the required permissions."
            ),
            "permission"
        )
        return

    if isinstance(original, discord.HTTPException):
        await send_context_error(
            ctx,
            "Discord Error",
            (
                "Discord encountered a problem while processing this request.\n\n"
                "Please try again in a moment."
            ),
            "error"
        )
        return

# UNKNOWN / INTERNAL ERRORS

    error_id = generate_error_id()

    log_error(
        original,
        error_id,
        command=ctx.command.qualified_name
        if ctx.command
        else None,
        user_id=ctx.author.id,
        guild_id=ctx.guild.id
        if ctx.guild
        else None,
        channel_id=ctx.channel.id
        if ctx.channel
        else None
    )

    await send_context_error(
        ctx,
        "Unexpected Error",
        (
            "Something went wrong while executing the command.\n\n"
            "Please try again later.\n\n"
            f"**Error ID:** `{error_id}`"
        ),
        "unexpected"
    )