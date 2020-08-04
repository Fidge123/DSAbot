import os
import random
import re

import discord

from bot import persistence, dice_roll, note, skill_check

TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
permittedChannels = []
userCharacters = {}
number_notes = {}
verbose = False
random.seed()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    channel_ids = persistence.load_channels()

    for channel_id in channel_ids:
        new = client.get_channel(channel_id[0])
        permittedChannels.append(new)

    notes = persistence.load_notes()
    for n in notes:
        number_notes[n[0]] = n[1]


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

        parsed_roll = dice_roll.parse(msgstring)
        if parsed_roll:
            return await send(dice_roll.create_response(parsed_roll, author))

        parsed_sc = skill_check.create_skill_check(msgstring, author)
        if parsed_sc:
            return await send(str(parsed_sc))

        number_code = note.parse(msgstring)
        if number_code:
            return await send(note.create_response(number_code, number_notes))

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
                response = str(number_notes)

            return await send(response)


def run():
    persistence.init_db()
    client.run(TOKEN)
