import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DATABASE_PATH = Path("data/errors/errors.db")


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialise_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS errors (
                error_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                message TEXT,
                command TEXT,
                user_id INTEGER,
                guild_id INTEGER,
                channel_id INTEGER,
                timestamp TEXT NOT NULL,
                traceback TEXT
            )
            """
        )

        connection.commit()


def save_error(
        error_id: str,
        error_type: str,
        message: str,
        traceback_text: str,
        *,
        command: str | None = None,
        user_id: int | None = None,
        guild_id: int | None = None,
        channel_id: int | None = None
):
    print(
        f"[ERROR DB] Saving {error_id}..."
    )

    print(
        f"[ERROR DB] Database path: "
        f"{DATABASE_PATH.resolve()}"
    )

    with get_connection() as connection:

        print("[ERROR DB] Connection opened.")

        connection.execute(
            """
            INSERT OR REPLACE INTO errors (
                error_id,
                type,
                message,
                command,
                user_id,
                guild_id,
                channel_id,
                timestamp,
                traceback
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                error_id,
                error_type,
                message,
                command,
                user_id,
                guild_id,
                channel_id,
                datetime.now(timezone.utc).isoformat(),
                traceback_text
            )
        )

        print("[ERROR DB] INSERT executed.")

        connection.commit()

        print("[ERROR DB] COMMIT completed.")

    print(
        f"[ERROR DB] Successfully saved {error_id}."
    )


def get_error(error_id: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM errors
            WHERE error_id = ?
            """,
            (error_id.upper(),)
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def delete_error(error_id: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM errors
            WHERE error_id = ?
            """,
            (error_id.upper(),)
        )

        connection.commit()

    return cursor.rowcount > 0