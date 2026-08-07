from .database import get_account
from .client import HoYoLabClient


def get_account_client(
    discord_user_id: int,
    genshin_uid: str
) -> HoYoLabClient | None:
    account = get_account(
        discord_user_id,
        genshin_uid
    )

    if account is None:
        return None

    client = HoYoLabClient(
        account["credentials"]
    )

    client.genshin_uid = account["genshin_uid"]
    client.genshin_server = account["genshin_server"]

    return client