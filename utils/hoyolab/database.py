import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .auth import HoYoLABCredentials
from .crypto import HoYoLABCrypto


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


def initialise_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                discord_user_id INTEGER NOT NULL,
                discord_username TEXT,
                discord_display_name TEXT,

                discord_guild_id INTEGER,
                discord_guild_name TEXT,

                nickname TEXT,
                cyrene_nickname TEXT,
                level INTEGER,

                genshin_uid TEXT NOT NULL,
                genshin_server TEXT NOT NULL,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                ltuid_v2 TEXT,
                ltoken_v2 TEXT,
                ltmid_v2 TEXT,

                cookie_token_v2 TEXT,
                account_mid_v2 TEXT,
                account_id_v2 TEXT,

                ltuid TEXT,
                ltoken TEXT,
                
                UNIQUE(discord_user_id, genshin_uid)
            )
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
    credentials: HoYoLABCredentials,
    *,
    discord_username: str | None = None,
    discord_display_name: str | None = None,
    discord_guild_id: int | None = None,
    discord_guild_name: str | None = None,
    genshin_uid: str,
    genshin_server: str,
    nickname: str | None = None,
    cyrene_nickname: str | None = None,
    level: int | None = None
) -> None:
    crypto = HoYoLABCrypto()

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

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO accounts (
                discord_user_id,
                discord_username,
                discord_display_name,
            
                discord_guild_id,
                discord_guild_name,
            
                nickname,
                cyrene_nickname,
                level,
            
                genshin_uid,
                genshin_server,
            
                created_at,
                updated_at,
            
                ltuid_v2,
                ltoken_v2,
                ltmid_v2,
            
                cookie_token_v2,
                account_mid_v2,
                account_id_v2,
            
                ltuid,
                ltoken
            )
            VALUES (
                ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?
            )

            ON CONFLICT(discord_user_id, genshin_uid)
            DO UPDATE SET
                discord_username = excluded.discord_username,
                discord_display_name = excluded.discord_display_name,
            
                discord_guild_id = excluded.discord_guild_id,
                discord_guild_name = excluded.discord_guild_name,
            
                nickname = excluded.nickname,
                cyrene_nickname = excluded.cyrene_nickname,
                level = excluded.level,
            
                genshin_server = excluded.genshin_server,
            
                updated_at = excluded.updated_at,
            
                ltuid_v2 = excluded.ltuid_v2,
                ltoken_v2 = excluded.ltoken_v2,
                ltmid_v2 = excluded.ltmid_v2,
            
                cookie_token_v2 = excluded.cookie_token_v2,
                account_mid_v2 = excluded.account_mid_v2,
                account_id_v2 = excluded.account_id_v2,
            
                ltuid = excluded.ltuid,
                ltoken = excluded.ltoken
            """,
            (
                discord_user_id,
                discord_username,
                discord_display_name,

                discord_guild_id,
                discord_guild_name,

                nickname,
                cyrene_nickname,
                level,

                genshin_uid,
                genshin_server,

                now,
                now,

                encrypted_ltuid_v2,
                encrypted_ltoken_v2,
                encrypted_ltmid_v2,

                encrypted_cookie_token_v2,
                encrypted_account_mid_v2,
                encrypted_account_id_v2,

                encrypted_ltuid,
                encrypted_ltoken
            )
        )

        connection.commit()


def get_accounts(
    discord_user_id: int
) -> list[dict]:
    crypto = HoYoLABCrypto()

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
        credentials = HoYoLABCredentials(
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
            ),
            ltuid=(
                crypto.decrypt(row["ltuid"])
                if row["ltuid"]
                else None
            ),
            ltoken=(
                crypto.decrypt(row["ltoken"])
                if row["ltoken"]
                else None
            )
        )

        accounts.append(
            {
                "id": row["id"],

                "discord_user_id": row["discord_user_id"],
                "discord_username": row["discord_username"],
                "discord_display_name": row["discord_display_name"],

                "discord_guild_id": row["discord_guild_id"],
                "discord_guild_name": row["discord_guild_name"],

                "credentials": credentials,

                "genshin_uid": row["genshin_uid"],
                "genshin_server": row["genshin_server"],
                "nickname": row["nickname"],
                "cyrene_nickname": row["cyrene_nickname"],
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
    crypto = HoYoLABCrypto()

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

    credentials = HoYoLABCredentials(
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
        ),
        ltuid=(
            crypto.decrypt(row["ltuid"])
            if row["ltuid"]
            else None
        ),
        ltoken=(
            crypto.decrypt(row["ltoken"])
            if row["ltoken"]
            else None
        )
    )

    return {
        "id": row["id"],

        "discord_user_id": row["discord_user_id"],
        "discord_username": row["discord_username"],
        "discord_display_name": row["discord_display_name"],

        "discord_guild_id": row["discord_guild_id"],
        "discord_guild_name": row["discord_guild_name"],

        "credentials": credentials,

        "genshin_uid": row["genshin_uid"],
        "genshin_server": row["genshin_server"],
        "nickname": row["nickname"],
        "cyrene_nickname": row["cyrene_nickname"],
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


def update_discord_user(
    discord_user_id: int,
    discord_username: str,
    discord_display_name: str,
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE accounts
            SET
                discord_username = ?,
                discord_display_name = ?
            WHERE discord_user_id = ?
            AND (
                discord_username IS NOT ?
                OR discord_display_name IS NOT ?
            )
            """,
            (
                discord_username,
                discord_display_name,
                discord_user_id,
                discord_username,
                discord_display_name
            )
        )

        connection.commit()

    return cursor.rowcount > 0


def update_discord_server(
    discord_user_id: int,
    discord_guild_id: int,
    discord_guild_name: str,
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE accounts
            SET
                discord_guild_id = ?,
                discord_guild_name = ?
            WHERE discord_user_id = ?
            AND (
                discord_guild_id IS NOT ?
                OR discord_guild_name IS NOT ?
            )
            """,
            (
                discord_guild_id,
                discord_guild_name,
                discord_user_id,
                discord_guild_id,
                discord_guild_name
            )
        )

        connection.commit()

    return cursor.rowcount > 0


def update_account_nickname(
    discord_user_id: int,
    genshin_uid: str,
    cyrene_nickname: str | None
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE accounts
            SET cyrene_nickname = ?
            WHERE discord_user_id = ?
            AND genshin_uid = ?
            """,
            (
                cyrene_nickname,
                discord_user_id,
                genshin_uid
            )
        )

        connection.commit()

    return cursor.rowcount > 0