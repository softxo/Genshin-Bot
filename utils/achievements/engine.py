from utils.achievements.models import Achievement


class AchievementEngine:

    def __init__(
        self,
        achievements: list[Achievement],
    ):
        self.achievements = achievements

        self._by_id = {
            achievement.id: achievement
            for achievement in achievements
        }

    # --------------------------------
    # FIND ACHIEVEMENT
    # --------------------------------

    def get(
        self,
        achievement_id: str,
    ) -> Achievement | None:

        return self._by_id.get(
            achievement_id
        )

    # --------------------------------
    # FIND ACHIEVEMENT OR RAISE
    # --------------------------------

    def require(
        self,
        achievement_id: str,
    ) -> Achievement:

        achievement = self.get(
            achievement_id
        )

        if achievement is None:
            raise KeyError(
                f"Achievement not found: "
                f"{achievement_id}"
            )

        return achievement

    # --------------------------------
    # SEARCH
    # --------------------------------

    def search(
        self,
        query: str,
    ) -> list[Achievement]:

        query = query.strip().lower()

        if not query:
            return []

        return [
            achievement
            for achievement in self.achievements
            if (
                query in achievement.name.lower()
                or query in achievement.id.lower()
                or query in achievement.category.lower()
            )
        ]

    # --------------------------------
    # CATEGORY
    # --------------------------------

    def get_category(
        self,
        category: str,
    ) -> list[Achievement]:

        return [
            achievement
            for achievement in self.achievements
            if achievement.category == category
        ]

    # --------------------------------
    # COUNTS
    # --------------------------------

    @property
    def achievement_count(self) -> int:

        return len(
            self.achievements
        )

    @property
    def tier_count(self) -> int:

        return sum(
            len(achievement.tiers)
            for achievement in self.achievements
        )