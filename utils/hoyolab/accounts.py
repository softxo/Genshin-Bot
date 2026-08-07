import genshin


async def get_genshin_accounts(
    client: genshin.Client
):
    return await client.get_game_accounts()