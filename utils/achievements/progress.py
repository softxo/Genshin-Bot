import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

PROGRESS_DIR = (
    BASE_DIR
    / "data"
    / "achievements"
    / "progress"
)


def get_progress_file(user_id: int) -> Path:
    return PROGRESS_DIR / f"{user_id}.json"


async def load_progress(
    user_id: int,
) -> dict:

    from utils.hoyolab.database import (
        get_achievement_progress
    )

    rows = await get_achievement_progress(
        user_id
    )

    progress = {}

    for row in rows:

        achievement_id = row["achievement_id"]
        tier = str(row["tier"])

        if achievement_id not in progress:
            progress[achievement_id] = {
                "tiers": {}
            }

        timestamp = None

        if row["completed_at"] is not None:
            timestamp = int(
                row["completed_at"].timestamp()
            )

        progress[achievement_id]["tiers"][tier] = {
            "completed": row["completed"],
            "current": row["current"],
            "timestamp": timestamp,
        }

    return progress


def save_progress(
    user_id: int,
    progress: dict,
) -> None:

    PROGRESS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = get_progress_file(user_id)

    with path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            progress,
            file,
            ensure_ascii=False,
            indent=2,
        )