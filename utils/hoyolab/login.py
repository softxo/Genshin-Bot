import genshin
from .errors import (
    HoYoLabAuthenticationError,
    HoYoLabAccountNotFoundError,
    HoYoLabAccountLockedError,
    HoYoLabAccountMutedError,
    HoYoLabVerificationError,
    HoYoLabCaptchaError,
    HoYoLabRateLimitError,
    HoYoLabUnexpectedError,
)


async def login_with_password(
    account: str,
    password: str
):
    client = genshin.Client()

    try:
        result = await client.login_with_password(
            account,
            password
        )

        return client, result

    except genshin.errors.AccountDoesNotExist as error:
        raise HoYoLabAccountNotFoundError from error

    except genshin.errors.AccountLoginFail as error:
        raise HoYoLabAuthenticationError from error

    except genshin.errors.AccountHasLocked as error:
        raise HoYoLabAccountLockedError from error

    except genshin.errors.AccountMuted as error:
        raise HoYoLabAccountMutedError from error

    except (
        genshin.errors.WrongOTP,
        genshin.errors.VerificationCodeRateLimited,
        genshin.errors.OTPRateLimited,
    ) as error:
        raise HoYoLabVerificationError from error

    except (
        genshin.errors.DailyGeetestTriggered,
        genshin.errors.GeetestError,
        genshin.errors.GeetestFailed,
    ) as error:
        raise HoYoLabCaptchaError from error

    except genshin.errors.TooManyRequests as error:
        raise HoYoLabRateLimitError from error


    except genshin.errors.GenshinException as error:
        print("===== HOYOLAB LOGIN ERROR =====")
        print(f"Type: {type(error).__name__}")
        print(f"Error: {error}")
        print("==============================")

        if "[-3006]" in str(error):
            raise HoYoLabRateLimitError from error

        raise HoYoLabUnexpectedError from error

    except Exception as error:
        print("===== UNEXPECTED LOGIN ERROR =====")
        print(f"Type: {type(error).__name__}")
        print(f"Error: {error}")
        print("==============================")

        raise HoYoLabUnexpectedError from error