import os
from typing import List, Tuple

from discord import TextChannel

DB_PATH = os.getenv("DATABASE_URL")
connection = None

if DB_PATH:
    import psycopg2

    connection = psycopg2.connect(DB_PATH, sslmode="require")
else:
    import sqlite3

    connection = sqlite3.connect("bot/persistence.db")

SCHEMA_PATH = "bot/schema.sql"


def init_db() -> bool:
    with open(SCHEMA_PATH, "r") as schemafile:
        commands = schemafile.read()
        connection.executescript(commands)
        connection.commit()
    return True


def persist_channel(channel: TextChannel) -> bool:
    connection.execute("INSERT OR REPLACE INTO channels VALUES (?)", (str(channel.id),))
    connection.commit()
    return True


def remove_channel(channel: TextChannel) -> bool:
    connection.execute("DELETE FROM channels WHERE id=?", (str(channel.id),))
    connection.commit()
    return True


def load_channels() -> List[Tuple[int]]:
    results = connection.execute("SELECT * FROM channels").fetchall()
    return results


def persist_note(note_id: str, value: int) -> bool:
    connection.execute(
        "INSERT OR REPLACE INTO numberNotes VALUES (?, ?)", (note_id, value)
    )
    connection.commit()
    return True


def remove_note(note_id: str) -> bool:
    connection.execute("DELETE FROM numberNotes WHERE id=?", (note_id,))
    connection.commit()
    return True


def load_notes() -> List[Tuple[str, int]]:
    results = connection.execute("SELECT * FROM numberNotes").fetchall()
    return results
