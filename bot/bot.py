import os
import random
import re

import discord

from bot import persistence, dice_roll, note, check, wiki, channel

TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
random.seed()


@client.event
async def on_ready() -> None:
    persistence.on_ready()
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message: discord.Message) -> None:
    msgstring: str = message.content.strip("` ")
    send = message.channel.send

    if message.author == client.user:
        return

    if channel.is_permitted(msgstring, message):
        if "DIE" in msgstring:
            await message.add_reaction("\U0001f480")
            await send("I shall die.")
            await client.close()
            return

        for create_response in [
            channel.create_response,
            dice_roll.create_response,
            check.create_response,
            note.create_response,
            wiki.create_response,
        ]:
            response = create_response(msgstring, message)
            if response:
                msg, embed = response
                return await send(msg, embed=embed)

        debug_code = re.search(
            r"^debug:(?P<debugCommand>[a-z]*)$", msgstring, re.IGNORECASE
        )
        if debug_code:
            if debug_code.group("debugCommand") == "cache":
                return await send("cache")

            if debug_code.group("debugCommand") == "fullCache":
                return await send("fullCache")

            if debug_code.group("debugCommand") == "numberNotes":
                return await send(str(note.number_notes))

            return await send("no debug")
    else:
        return await send("I am listening for rolls here")


def run() -> None:
    client.run(TOKEN)
