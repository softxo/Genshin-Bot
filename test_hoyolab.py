import asyncio
from dotenv import load_dotenv
from utils.hoyolab.account_client import get_account_client

load_dotenv()

DISCORD_USER_ID = 718579165938319421
GENSHIN_UID = "774182513"


async def main():
    client = get_account_client(
        DISCORD_USER_ID,
        GENSHIN_UID
    )

    if client is None:
        print("Account not found.")
        return

    print("Account found.")
    print("Creating HoYoLab client...")

    async with client:
        print("Client connected.")
        result = await client.get_game_roles()

        daily_note = await client.get_genshin_daily_note(
            client.genshin_uid,
            client.genshin_server
        )

        print("===== DAILY NOTE =====")
        print(daily_note)
        print("======================")

    print("===== RESULT =====")
    print(result)
    print("==================")


asyncio.run(main())