import os
import sqlite3
from typing import List, Tuple

import psycopg2
from discord import TextChannel

DB_PATH = os.getenv("DATABASE_URL")
is_sqlite = False if DB_PATH else True


def conn():
    if DB_PATH:
        return psycopg2.connect(DB_PATH, sslmode="require")
    else:
        return sqlite3.connect("bot/persistence.db")


SCHEMA_PATH = "bot/schema.sql"


def init_db() -> bool:
    with conn() as connection:
        cursor = connection.cursor()
        if is_sqlite:
            cursor.executescript(open(SCHEMA_PATH).read())
        else:
            cursor.execute(open(SCHEMA_PATH).read())
        connection.commit()
        cursor.close()
    return True


def persist_channel(channel: TextChannel) -> bool:
    sqlite = "INSERT OR REPLACE INTO channels VALUES (?)"
    psql = "INSERT INTO channels VALUES (%s) ON CONFLICT DO NOTHING"

    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute(sqlite if is_sqlite else psql, (str(channel.id),))
        connection.commit()
        cursor.close()
    return True


def remove_channel(channel: TextChannel) -> bool:
    sqlite = "DELETE FROM channels WHERE id=?"
    psql = "DELETE FROM channels WHERE id=%s"

    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute(sqlite if is_sqlite else psql, (str(channel.id),))
        connection.commit()
        cursor.close()
    return True


def load_channels() -> List[Tuple[int]]:
    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM channels")
        return cursor.fetchall()


def persist_note(note_id: str, value: int) -> bool:
    sqlite = "INSERT OR REPLACE numberNotes VALUES (?, ?)"
    psql = "INSERT INTO numberNotes(id, content) VALUES (%s, %s) ON CONFLICT(id) DO UPDATE SET content=excluded.content"
    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute(sqlite if is_sqlite else psql, (note_id, value,))
        connection.commit()
        cursor.close()
    return True


def remove_note(note_id: str) -> bool:
    sqlite = "DELETE FROM numberNotes WHERE id=?"
    psql = "DELETE FROM numberNotes WHERE id=%s"
    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute(sqlite if is_sqlite else psql, (note_id,))
        connection.commit()
        cursor.close()
    return True


def load_notes() -> List[Tuple[str, int]]:
    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM numberNotes")
        return cursor.fetchall()
