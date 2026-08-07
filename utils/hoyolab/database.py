import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .auth import HoYoLabCredentials
from .crypto import HoYoLabCrypto


DATABASE_PATH = Path("data/hoyolab/hoyolab.db")


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
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                discord_user_id INTEGER NOT NULL,

                ltuid TEXT,
                ltoken TEXT,

                ltuid_v2 TEXT,
                ltoken_v2 TEXT,
                ltmid_v2 TEXT,
                
                cookie_token_v2 TEXT,
                account_mid_v2 TEXT,
                account_id_v2 TEXT,

                genshin_uid TEXT NOT NULL,
                genshin_server TEXT NOT NULL,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE(discord_user_id, genshin_uid)
            )
            """
        )

        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(accounts)"
            ).fetchall()
        }

        new_columns = {
            "cookie_token_v2": "TEXT",
            "account_mid_v2": "TEXT",
            "account_id_v2": "TEXT",
            "nickname": "TEXT",
            "level": "INTEGER"
        }

        for column, column_type in new_columns.items():
            if column not in existing_columns:
                connection.execute(
                    f"""
                    ALTER TABLE accounts
                    ADD COLUMN {column} {column_type}
                    """
                )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_accounts_discord_user
            ON accounts(discord_user_id)
            """
        )

        connection.commit()


def save_account(
    discord_user_id: int,
    credentials: HoYoLabCredentials,
    *,
    genshin_uid: str,
    genshin_server: str,
    nickname: str | None = None,
    level: int | None = None
):
    crypto = HoYoLabCrypto()

    encrypted_ltuid = (
        crypto.encrypt(credentials.ltuid)
        if credentials.ltuid
        else None
    )

    encrypted_ltoken = (
        crypto.encrypt(credentials.ltoken)
        if credentials.ltoken
        else None
    )

    encrypted_ltuid_v2 = (
        crypto.encrypt(credentials.ltuid_v2)
        if credentials.ltuid_v2
        else None
    )

    encrypted_ltoken_v2 = (
        crypto.encrypt(credentials.ltoken_v2)
        if credentials.ltoken_v2
        else None
    )

    encrypted_ltmid_v2 = (
        crypto.encrypt(credentials.ltmid_v2)
        if credentials.ltmid_v2
        else None
    )

    encrypted_cookie_token_v2 = (
        crypto.encrypt(credentials.cookie_token_v2)
        if credentials.cookie_token_v2
        else None
    )

    encrypted_account_mid_v2 = (
        crypto.encrypt(credentials.account_mid_v2)
        if credentials.account_mid_v2
        else None
    )

    encrypted_account_id_v2 = (
        crypto.encrypt(credentials.account_id_v2)
        if credentials.account_id_v2
        else None
    )

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO accounts (
                discord_user_id,
                
                ltuid,
                ltoken,
                
                ltuid_v2,
                ltoken_v2,
                ltmid_v2,
                
                cookie_token_v2,
                account_mid_v2,
                account_id_v2,
                
                genshin_uid,
                genshin_server,
                
                nickname,
                level,
                
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(discord_user_id, genshin_uid)
            DO UPDATE SET
                ltuid = excluded.ltuid,
                ltoken = excluded.ltoken,

                ltuid_v2 = excluded.ltuid_v2,
                ltoken_v2 = excluded.ltoken_v2,
                ltmid_v2 = excluded.ltmid_v2,
            
                cookie_token_v2 = excluded.cookie_token_v2,
                account_mid_v2 = excluded.account_mid_v2,
                account_id_v2 = excluded.account_id_v2,
            
                genshin_server = excluded.genshin_server,
                nickname = excluded.nickname,
                level = excluded.level,
                
                updated_at = excluded.updated_at
            """,
            (
                discord_user_id,

                encrypted_ltuid,
                encrypted_ltoken,

                encrypted_ltuid_v2,
                encrypted_ltoken_v2,
                encrypted_ltmid_v2,

                encrypted_cookie_token_v2,
                encrypted_account_mid_v2,
                encrypted_account_id_v2,

                genshin_uid,
                genshin_server,

                nickname,
                level,

                now,
                now
            )
        )

        connection.commit()


def get_accounts(
    discord_user_id: int
) -> list[dict]:
    crypto = HoYoLabCrypto()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM accounts
            WHERE discord_user_id = ?
            ORDER BY created_at ASC
            """,
            (discord_user_id,)
        ).fetchall()

    accounts = []

    for row in rows:
        credentials = HoYoLabCredentials(
            ltuid=(
                crypto.decrypt(row["ltuid"])
                if row["ltuid"]
                else None
            ),
            ltoken=(
                crypto.decrypt(row["ltoken"])
                if row["ltoken"]
                else None
            ),
            ltuid_v2=(
                crypto.decrypt(row["ltuid_v2"])
                if row["ltuid_v2"]
                else None
            ),
            ltoken_v2=(
                crypto.decrypt(row["ltoken_v2"])
                if row["ltoken_v2"]
                else None
            ),
            ltmid_v2=(
                crypto.decrypt(row["ltmid_v2"])
                if row["ltmid_v2"]
                else None
            ),
            cookie_token_v2=(
                crypto.decrypt(row["cookie_token_v2"])
                if row["cookie_token_v2"]
                else None
            ),
            account_mid_v2=(
                crypto.decrypt(row["account_mid_v2"])
                if row["account_mid_v2"]
                else None
            ),
            account_id_v2=(
                crypto.decrypt(row["account_id_v2"])
                if row["account_id_v2"]
                else None
            )
        )

        accounts.append(
            {
                "id": row["id"],
                "credentials": credentials,
                "genshin_uid": row["genshin_uid"],
                "genshin_server": row["genshin_server"],
                "nickname": row["nickname"],
                "level": row["level"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        )

    return accounts

def get_account(
    discord_user_id: int,
    genshin_uid: str
) -> dict | None:
    crypto = HoYoLabCrypto()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM accounts
            WHERE discord_user_id = ?
            AND genshin_uid = ?
            LIMIT 1
            """,
            (
                discord_user_id,
                genshin_uid
            )
        ).fetchone()

    if row is None:
        return None

    credentials = HoYoLabCredentials(
        ltuid=(
            crypto.decrypt(row["ltuid"])
            if row["ltuid"]
            else None
        ),
        ltoken=(
            crypto.decrypt(row["ltoken"])
            if row["ltoken"]
            else None
        ),
        ltuid_v2=(
            crypto.decrypt(row["ltuid_v2"])
            if row["ltuid_v2"]
            else None
        ),
        ltoken_v2=(
            crypto.decrypt(row["ltoken_v2"])
            if row["ltoken_v2"]
            else None
        ),
        ltmid_v2=(
            crypto.decrypt(row["ltmid_v2"])
            if row["ltmid_v2"]
            else None
        ),
        cookie_token_v2=(
            crypto.decrypt(row["cookie_token_v2"])
            if row["cookie_token_v2"]
            else None
        ),
        account_mid_v2=(
            crypto.decrypt(row["account_mid_v2"])
            if row["account_mid_v2"]
            else None
        ),
        account_id_v2=(
            crypto.decrypt(row["account_id_v2"])
            if row["account_id_v2"]
            else None
        )
    )

    return {
        "id": row["id"],
        "credentials": credentials,
        "genshin_uid": row["genshin_uid"],
        "genshin_server": row["genshin_server"],
        "nickname": row["nickname"],
        "level": row["level"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }


def get_account_count(
    discord_user_id: int
) -> int:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM accounts
            WHERE discord_user_id = ?
            """,
            (discord_user_id,)
        ).fetchone()

    return row["count"]


def account_exists(
    discord_user_id: int,
    genshin_uid: str
) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM accounts
            WHERE discord_user_id = ?
            AND genshin_uid = ?
            LIMIT 1
            """,
            (
                discord_user_id,
                genshin_uid
            )
        ).fetchone()

    return row is not None


def delete_account(
    discord_user_id: int,
    genshin_uid: str
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM accounts
            WHERE discord_user_id = ?
            AND genshin_uid = ?
            """,
            (
                discord_user_id,
                genshin_uid
            )
        )

        connection.commit()

    return cursor.rowcount > 0