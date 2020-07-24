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

        skill_check = re.search(
            r"^!?(?P<first>[0-9]+),\s?(?P<second>[0-9]+),\s?(?P<third>[0-9]+)\s?(@\s?(?P<skill>[0-9]+))?$",
            msgstring,
            re.IGNORECASE,
        )
        if skill_check:
            skill_req = 0

            rolls = [
                {
                    "attr": int(skill_check.group("first")),
                    "roll": random.randint(1, 20),
                },
                {
                    "attr": int(skill_check.group("second")),
                    "roll": random.randint(1, 20),
                },
                {
                    "attr": int(skill_check.group("third")),
                    "roll": random.randint(1, 20),
                },
            ]
            skill_req = sum(map(lambda x: max([x["roll"] - x["attr"], 0]), rolls))

            response = "{author}\n{roll1}, {roll2}, {roll3} ===> {skill_req}".format(
                author=author.mention,
                roll1=rolls[0]["roll"],
                roll2=rolls[1]["roll"],
                roll3=rolls[2]["roll"],
                skill_req=-skill_req,
            )

            if skill_check.group("skill"):
                skill_level = int(skill_check.group("skill"))
                remainder = skill_level - skill_req
                response += "\n({skill_level} - {skill_req} = {FP})".format(
                    skill_level=skill_level,
                    skill_req=skill_req,
                    FP=skill_level - skill_req,
                )
                if remainder < 0:
                    response += " QS: 0 FAIL"
                else:
                    response += " QS: {}".format(remainder // 3 + 1)

            await send(response)


if __name__ == "__main__":
    persistence.init_db()
    client.run(TOKEN)
