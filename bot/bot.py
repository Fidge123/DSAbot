import os
import random

import discord

from bot import persistence, dice_roll, note, check, wiki, channel, stats

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

    if channel.is_permitted(message.channel.id) or isinstance(
        message.channel, discord.channel.DMChannel
    ):
        if (
            "DIE" == message.content
            and message.author == (await client.application_info()).owner
        ):
            await message.add_reaction("\U0001f480")
            await message.channel.send("I shall die.")
            return await client.close()

        if "help" == message.content.lower():
            return await message.channel.send(
                message.author.mention
                + " Würfelhelfer: https://fidge123.github.io/DSAbot/"
            )

        for create_response in [
            channel.create_response,
            check.create_response,
            note.create_response,
            wiki.create_response,
            stats.create_response,
            dice_roll.create_response,
        ]:
            response = create_response(message)
            if response:
                return await response.send()
    else:
        return await channel.add_channel(message)


def run() -> None:
    client.run(TOKEN)
