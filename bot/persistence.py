import sqlite3
from typing import List, Tuple

from discord import TextChannel

DB_PATH = "bot/persistence.db"
SCHEMA_PATH = "bot/schema.sql"


def init_db() -> bool:
    with open(SCHEMA_PATH, "r") as schemafile:
        commands = schemafile.read()

    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(commands)
        connection.commit()

    return True


def persist_channel(channel: TextChannel) -> bool:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO channels VALUES (?)", (str(channel.id),)
        )
        connection.commit()

    return True


def remove_channel(channel: TextChannel) -> bool:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("DELETE FROM channels WHERE id=?", (str(channel.id),))
        connection.commit()

    return True


def load_channels() -> List[Tuple[int]]:
    with sqlite3.connect(DB_PATH) as connection:
        results = connection.execute("SELECT * FROM channels").fetchall()

    return results


def persist_note(note_id: str, value: int) -> bool:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO numberNotes VALUES (?, ?)", (note_id, value)
        )
        connection.commit()

    return True


def remove_note(note_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("DELETE FROM numberNotes WHERE id=?", (note_id,))
        connection.commit()
    return True


def load_notes() -> List[Tuple[str, int]]:
    with sqlite3.connect(DB_PATH) as connection:
        results = connection.execute("SELECT * FROM numberNotes").fetchall()

    return results
