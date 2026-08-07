import discord
from utils.constants.emojis import ERROR_EMOJIS, ERROR_TYPE_EMOJIS
from utils.constants.colours import ERROR_COLOURS, ERROR_TYPE_COLOURS


class HoYoLabError(Exception):
    """Base exception for HoYoLab-related errors."""


class HoYoLabAuthenticationError(HoYoLabError):
    """HoYoLab credentials were rejected."""


class HoYoLabAccountNotFoundError(HoYoLabError):
    """The HoYoLab account could not be found."""


class HoYoLabAccountLockedError(HoYoLabError):
    """The HoYoLab account is locked."""


class HoYoLabAccountMutedError(HoYoLabError):
    """The HoYoLab account is restricted."""


class HoYoLabVerificationError(HoYoLabError):
    """HoYoLab verification failed or was rate-limited."""


class HoYoLabCaptchaError(HoYoLabError):
    """HoYoLab CAPTCHA verification failed or is required."""


class HoYoLabRateLimitError(HoYoLabError):
    """HoYoLab rate-limited the request."""


class HoYoLabCookieError(HoYoLabError):
    """The HoYoLab cookies are invalid."""


class HoYoLabConnectionError(HoYoLabError):
    """A connection to HoYoLab could not be established."""


class HoYoLabUnexpectedError(HoYoLabError):
    """An unexpected HoYoLab error occurred."""


def build_hoyolab_error_embed(
    error_type: str,
    title: str,
    description: str
) -> discord.Embed:
    
    emoji = ERROR_TYPE_EMOJIS.get(
        error_type,
        ERROR_EMOJIS.get(error_type, ERROR_EMOJIS["error"])
    )

    colour = ERROR_TYPE_COLOURS.get(
        error_type,
        ERROR_COLOURS.get(error_type, ERROR_COLOURS["error"])
    )

    return discord.Embed(
        title=f"{emoji} {title}",
        description=description,
        color=colour
    )