import aiohttp
import genshin
from .auth import HoYoLABCredentials



class HoYoLABClient:
    BASE_URL = "https://bbs-api-os.hoyolab.com"

    def __init__(
            self,
            credentials: HoYoLABCredentials
    ):
        self.credentials = credentials
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            cookies=self.credentials.as_cookies(),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/149.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
            }
        )

        return self

    async def __aexit__(
            self,
            exc_type,
            exc,
            tb
    ):
        if self.session:
            await self.session.close()

    async def get_game_roles(self) -> dict:
        if self.session is None:
            raise RuntimeError(
                "HoYoLABClient must be used with 'async with'."
            )

        url = (
            "https://api-account-os.hoyolab.com/"
            "account/binding/api/"
            "getUserGameRolesByCookieToken"
        )

        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def get_genshin_daily_note(
            self,
            genshin_uid: str,
            genshin_server: str
    ) -> dict:
        if self.session is None:
            raise RuntimeError(
                "HoYoLABClient must be used with 'async with'."
            )

        url = (
            "https://sg-public-api.hoyolab.com/"
            "event/game_record/genshin/api/dailyNote"
        )

        params = {
            "role_id": genshin_uid,
            "server": genshin_server
        }

        async with self.session.get(
                url,
                params=params
        ) as response:

            response.raise_for_status()

            return await response.json()

    async def get_imaginarium_theater(self) -> dict:
        client = genshin.Client(
            cookies=self.credentials.as_cookies()
        )

        return await client.get_imaginarium_theater(
            raw=True
        )

    async def get_genshin_spiral_abyss(self) -> genshin.models.SpiralAbyss:
        client = genshin.Client(
            cookies=self.credentials.as_cookies()
        )

        return await client.get_genshin_spiral_abyss()