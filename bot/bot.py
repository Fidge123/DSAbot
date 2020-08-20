import os
import random
import re

from typing import List

import discord

from bot import persistence, dice_roll, note, check, wiki

TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
permittedChannels: List[discord.TextChannel] = []
random.seed()


@client.event
async def on_ready() -> None:
    print(f"{client.user} has connected to Discord!")
    note.on_load()
    channel_ids = persistence.load_channels()

    for channel_id in channel_ids:
        new = client.get_channel(channel_id[0])
        permittedChannels.append(new)


@client.event
async def on_message(message: discord.Message) -> None:
    msgstring: str = message.content.strip("` ")
    send = message.channel.send
    author: discord.member.Member = message.author
    channel: discord.TextChannel = message.channel

    if message.author == client.user:
        return

    if "SUMMON" in msgstring:
        if channel not in permittedChannels:
            permittedChannels.append(channel)
            persistence.persist_channel(channel)
            return await send("I am listening for rolls here")
        else:
            return await send("I am already listening")

    if channel in permittedChannels:

        if "BEGONE" in msgstring:
            permittedChannels.remove(channel)
            persistence.remove_channel(channel)
            await send("I have left")

        if "DIE" in msgstring:
            await message.add_reaction("\U0001f480")
            await send("I shall die.")
            await client.close()
            return

        for create_response in [
            dice_roll.create_response,
            check.create_response,
            note.create_response,
            wiki.create_response,
        ]:
            response = create_response(msgstring, author)
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


def run() -> None:
    persistence.init_db()
    client.run(TOKEN)
