import sqlite3
import discord

def init_db():

    with open("schema.sql", "r")as schemafile:
        commands = schemafile.read()

    with sqlite3.connect("persistence.db") as connection:
        connection.execute(commands)
        connection.commit()

    return True


def persist_channel(channel):
    
    with sqlite3.connect("persistence.db") as connection:
        connection.execute("INSERT INTO channels VALUES (?)", (str(channel.id),) )
        connection.commit()

    return True

def remove_channel(channel):

    with sqlite3.connect("persistence.db") as connection:
        connection.execute("DELETE FROM channels WHERE id=?", (str(channel.id),) )
        connection.commit()

    return True

def load_channels():

    allowed_channels= []
    
    with sqlite3.connect("persistence.db") as connection:
        results = connection.execute("SELECT * FROM channels").fetchall()

    return results
