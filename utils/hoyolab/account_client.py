from .database import get_account
from .client import HoYoLABClient


_client_cache: dict[
    tuple[int, str],
    HoYoLABClient
] = {}


async def get_account_client(
    discord_user_id: int,
    genshin_uid: str
) -> HoYoLABClient | None:
    cache_key = (
        discord_user_id,
        genshin_uid
    )

    cached_client = _client_cache.get(cache_key)

    if cached_client is not None:
        return cached_client

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

    _client_cache[cache_key] = client

    return client