import os
import random

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
    if message.author == client.user:
        return

    if channel.is_permitted(message):
        if "DIE" == message.content and str(message.author) == "fidge123#3686":
            await message.add_reaction("\U0001f480")
            await message.channel.send("I shall die.")
            return await client.close()

        for create_response in [
            channel.create_response,
            dice_roll.create_response,
            check.create_response,
            note.create_response,
            wiki.create_response,
        ]:
            response = create_response(message)
            if response:
                msg, embed = response
                return await message.channel.send(msg, embed=embed)


def run() -> None:
    client.run(TOKEN)
