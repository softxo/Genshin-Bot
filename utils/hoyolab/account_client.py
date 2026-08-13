from .database import get_account
from .client import HoYoLABClient


async def get_account_client(
    discord_user_id: int,
    genshin_uid: str
) -> HoYoLABClient | None:

    account = await get_account(
        discord_user_id,
        genshin_uid
    )

    if account is None:
        return None

    client = HoYoLABClient(
        account["credentials"]
    )

    client.genshin_uid = account["genshin_uid"]
    client.genshin_server = account["genshin_server"]

    return client