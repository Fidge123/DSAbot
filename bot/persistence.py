import os
import sqlite3
from typing import List, Tuple

import psycopg2
from discord import TextChannel

DB_PATH = os.getenv("DATABASE_URL")


def conn():
    if DB_PATH:
        return psycopg2.connect(DB_PATH, sslmode="require")
    else:
        return sqlite3.connect("bot/persistence.db")


SCHEMA_PATH = "bot/schema.sql"


def init_db() -> bool:
    with conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute(open(SCHEMA_PATH).read())
            connection.commit()
    return True


def persist_channel(channel: TextChannel) -> bool:
    with conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO channels VALUES (?) ON CONFLICT DO NOTHING",
                (str(channel.id),),
            )
            connection.commit()
    return True


def remove_channel(channel: TextChannel) -> bool:
    with conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM channels WHERE id=?", (str(channel.id),))
            connection.commit()
    return True


def load_channels() -> List[Tuple[int]]:
    with conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM channels")
            return cursor.fetchall()


def persist_note(note_id: str, value: int) -> bool:
    with conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO numberNotes(id, content) VALUES (?, ?)  ON CONFLICT(id) DO UPDATE SET content=excluded.content",
                (note_id, value),
            )
            connection.commit()
    return True


def remove_note(note_id: str) -> bool:
    with conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM numberNotes WHERE id=?", (note_id,))
            connection.commit()
    return True


def load_notes() -> List[Tuple[str, int]]:
    with conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM numberNotes")
            return cursor.fetchall()
