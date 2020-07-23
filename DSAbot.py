import os
import random
import re

import discord

import persistence

TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
permittedChannels = []
userCharacters = {}
verbose = False
random.seed()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
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
            if channel in permittedChannels:
                permittedChannels.remove(channel)
                persistence.remove_channel(channel)
                await send("I have left")

        if "DIE" in msgstring:
            await message.add_reaction("\U0001f480")
            await send("I shall die.")
            await client.close()
            return

        dicecode = re.search(
            r"^!*(?P<amount>[0-9]+)[dw](?P<sides>[0-9]+)$", msgstring, re.IGNORECASE
        )
        if dicecode:
            dieamount = int(dicecode.group("amount"))
            diesides = int(dicecode.group("sides"))
            response = author.mention + "\n"

            for _ in range(dieamount):
                roll = random.randint(1, diesides)
                response += str(roll) + ", "

            response = response[:-2]

            await send(response)

        if re.search(r"^([0-9]+,\s*)*[0-9]+(@[0-9]+)*$", msgstring):
            diestring = msgstring
            diestring.replace(" ", "")
            skill_level = False

            if "@" in diestring:
                skill_split = diestring.split("@")
                skill_level = int(skill_split[1])
                diestring = skill_split[0]

            diesplit = diestring.split(",")

            response = author.mention + "\n"
            skill_req = 0

            for attr in diesplit:
                roll = random.randint(1, 20)
                result = roll - int(attr)

                if result < 0:
                    result = 0

                response += str(roll) + ", "
                skill_req += result
            response = response[:-2]

            response += " ===> " + str(-skill_req)

            if skill_level:
                remainder = skill_level - skill_req
                response += "\n(" + str(skill_level) + " - " + str(skill_req) + ") "
                if remainder < 0:
                    response += "QS: 0 FAIL"
                else:
                    response += "QS: " + str(remainder // 3 + 1)

            await send(response)


if __name__ == "__main__":
    persistence.init_db()
    client.run(TOKEN)
