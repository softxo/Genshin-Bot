import json
from pathlib import Path

from utils.achievements.achievements import load_achievements
from utils.achievements.progress import save_progress


BASE_DIR = Path(__file__).resolve().parents[2]


def import_achievements(
    user_id: int,
    export_file: str | Path,
) -> dict:

    export_path = Path(export_file)

    if not export_path.exists():
        raise FileNotFoundError(
            f"Achievement export not found: {export_path}"
        )

    # --------------------------------
    # Load YaeAchievement export
    # --------------------------------

    with export_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        export_data = json.load(file)

    exported_achievements = export_data.get(
        "list",
        []
    )

    if not isinstance(exported_achievements, list):
        raise ValueError(
            "Invalid achievement export."
        )

    # --------------------------------
    # Load Cyrene achievements
    # --------------------------------

    achievements = load_achievements()

    # --------------------------------
    # Build Genshin ID -> achievement
    # + tier map
    # --------------------------------

    achievement_map = {}

    for achievement in achievements:

        achievement_id = achievement.get(
            "id"
        )

        genshin_ids = achievement.get(
            "genshin_ids",
            []
        )

        tiers = achievement.get(
            "tiers",
            []
        )

        if not isinstance(genshin_ids, list):
            continue

        if not isinstance(tiers, list):
            continue

        for index, genshin_id in enumerate(
            genshin_ids
        ):

            if index >= len(tiers):
                break

            tier = tiers[index]

            achievement_map[
                str(genshin_id)
            ] = {
                "achievement_id": achievement_id,
                "tier": tier.get("tier"),
            }

    # --------------------------------
    # Import progress
    # --------------------------------

    progress = {}

    matched = 0
    unmatched = 0

    for entry in exported_achievements:

        if not isinstance(entry, dict):
            continue

        genshin_id = entry.get("id")

        if genshin_id is None:
            continue

        genshin_id = str(genshin_id)

        mapping = achievement_map.get(
            genshin_id
        )

        if mapping is None:
            unmatched += 1
            continue

        achievement_id = mapping[
            "achievement_id"
        ]

        tier_number = mapping[
            "tier"
        ]

        # Create achievement entry
        if achievement_id not in progress:

            progress[achievement_id] = {
                "tiers": {}
            }

        # Store this tier's progress
        progress[
            achievement_id
        ][
            "tiers"
        ][
            str(tier_number)
        ] = {
            "completed": entry.get(
                "status"
            ) == 3,
            "current": entry.get(
                "current",
                0
            ),
            "timestamp": entry.get(
                "timestamp"
            ),
        }

        matched += 1

    # --------------------------------
    # Save
    # --------------------------------

    save_progress(
        user_id,
        progress,
    )

    return {
        "matched": matched,
        "unmatched": unmatched,
        "total": len(exported_achievements),
    }


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m "
            "utils.achievements.importer "
            "<export_file>"
        )
        raise SystemExit(1)

    export_file = Path(
        sys.argv[1]
    )

    result = import_achievements(
        user_id=1,
        export_file=export_file,
    )

    print(result)