import sqlite3


def init_db():
    with open("schema.sql", "r") as schemafile:
        commands = schemafile.read()

    with sqlite3.connect("persistence.db") as connection:
        connection.executescript(commands)
        connection.commit()

    return True


def persist_channel(channel):
    with sqlite3.connect("persistence.db") as connection:
        connection.execute("INSERT OR REPLACE INTO channels VALUES (?)", (str(channel.id),))
        connection.commit()

    return True


def remove_channel(channel):
    with sqlite3.connect("persistence.db") as connection:
        connection.execute("DELETE FROM channels WHERE id=?", (str(channel.id),))
        connection.commit()

    return True


def load_channels():
    with sqlite3.connect("persistence.db") as connection:
        results = connection.execute("SELECT * FROM channels").fetchall()

    return results

def persist_note(noteID, value):
    with sqlite3.connect("persistence.db") as connection:
        connection.execute("INSERT OR REPLACE INTO numberNotes VALUES (?, ?)", (noteID, value,))
        connection.commit()

    return True

def remove_note(noteID):
    with sqlite3.connect("persistence.db") as connection:
        connection.execute("DELETE FROM numberNotes WHERE id=?", (noteID,))
        connection.commit()
    return True

def load_notes():
    with sqlite3.connect("persistence.db") as connection:
        results = connection.execute("SELECT * FROM numberNotes").fetchall()

    return results
