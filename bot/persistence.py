import sqlite3
from typing import List, Tuple

from discord import TextChannel

db_path = "bot/persistence.db"
schema_path = "bot/schema.sql"


def init_db() -> bool:
    with open(schema_path, "r") as schemafile:
        commands = schemafile.read()

    with sqlite3.connect(db_path) as connection:
        connection.executescript(commands)
        connection.commit()

    return True


def persist_channel(channel: TextChannel) -> bool:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO channels VALUES (?)", (str(channel.id),)
        )
        connection.commit()

    return True


def remove_channel(channel: TextChannel) -> bool:
    with sqlite3.connect(db_path) as connection:
        connection.execute("DELETE FROM channels WHERE id=?", (str(channel.id),))
        connection.commit()

    return True


def load_channels() -> List[Tuple[int]]:
    with sqlite3.connect(db_path) as connection:
        results = connection.execute("SELECT * FROM channels").fetchall()

    return results


def persist_note(noteID: str, value: int) -> bool:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO numberNotes VALUES (?, ?)", (noteID, value)
        )
        connection.commit()

    return True


def remove_note(noteID: str) -> bool:
    with sqlite3.connect(db_path) as connection:
        connection.execute("DELETE FROM numberNotes WHERE id=?", (noteID,))
        connection.commit()
    return True


def load_notes() -> List[Tuple[str, int]]:
    with sqlite3.connect(db_path) as connection:
        results = connection.execute("SELECT * FROM numberNotes").fetchall()

    return results
