import os
import random
import re

import discord

from bot import persistence, dice_roll, note, check

TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
permittedChannels = []
random.seed()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    note.on_load()
    channel_ids = persistence.load_channels()

    for channel_id in channel_ids:
        new = client.get_channel(channel_id[0])
        permittedChannels.append(new)


@client.event
async def on_message(message: discord.Message):
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
            await send("I am listening for rolls here")
        else:
            await send("I am already listening")

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

        response = dice_roll.create_response(msgstring, author)
        if response:
            return await send(response)

        response = check.create_response(msgstring, author)
        if response:
            return await send(response)

        response = note.create_response(msgstring, author)
        if response:
            return await send(response)

        debug_code = re.search(
            r"^debug:(?P<debugCommand>[a-z]*)$", msgstring, re.IGNORECASE
        )
        if debug_code:
            response = "no debug"

            if debug_code.group("debugCommand") == "cache":
                response = "cache"

            if debug_code.group("debugCommand") == "fullCache":
                response = "fullCache"

            if debug_code.group("debugCommand") == "numberNotes":
                response = str(note.number_notes)

            return await send(response)


def run():
    persistence.init_db()
    client.run(TOKEN)
