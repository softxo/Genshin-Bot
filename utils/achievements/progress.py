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


def load_progress(user_id: int) -> dict:
    path = get_progress_file(user_id)

    if not path.exists():
        return {}

    try:
        with path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {}


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