import asyncio
import selectors

from dotenv import load_dotenv

from utils.hoyolab.database import initialise_database
from utils.achievements.state import load_achievement_state


load_dotenv()


async def main():

    await initialise_database()

    achievements = await load_achievement_state(
        user_id=1
    )

    print(
        f"Loaded achievements: {len(achievements)}"
    )

    for achievement in achievements:

        print()
        print(
            achievement["name"]
        )

        print(
            f"  ID: {achievement['id']}"
        )

        print(
            f"  Category: {achievement['category']}"
        )

        tiers = achievement.get(
            "tiers",
            []
        )

        print(
            f"  Tiers: {len(tiers)}"
        )

        for tier in tiers:

            print(
                f"    Tier {tier['tier']}: "
                f"{tier.get('current', 0)}/"
                f"{tier.get('progress', 0)} "
                f"| Completed: "
                f"{tier.get('completed', False)}"
            )


if __name__ == "__main__":

    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        )
    )