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
            r"^!?(?P<amount>[0-9]+)[dw](?P<sides>[0-9]+)$", msgstring, re.IGNORECASE
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

        # The regex matches the following:
        # 1. Optional exclamation mark
        # 2. A non-zero amount of numbers followed by comma or space (captured as `attr`)
        # 3. An @ followed by a number (captured as `FW`)
        # 4. A + modifier (captured as `add`)
        # 5. A - modifier (captured as `sub`)

        skill_check = re.search(
            r"^!?(?P<attr>(?:[0-9]+,?\ ?)+)\ ?(?:@\ ?(?P<FW>[0-9]+))?\ ?(?:\+\ ?(?P<add>[0-9]+))?(?:\-\ ?(?P<sub>[0-9]+))?$",
            msgstring,
            re.IGNORECASE,
        )

        if skill_check:

            # sanitize special characters and split into list of numbers
            attributes = (
                skill_check.group("attr")
                .strip()
                .replace(",", " ")
                .replace("  ", " ")
                .split(" ")
            )
            rolls = []
            add = int(skill_check.group("add") or 0)
            sub = int(skill_check.group("sub") or 0)

            for attr in attributes:
                rolls.append(
                    {"attr": int(attr), "roll": random.randint(1, 20),}
                )

            skill_req = sum(
                map(lambda x: max([x["roll"] - x["attr"] - add + sub, 0]), rolls)
            )

            response = "{author}\n{rolls} ===> {skill_req}".format(
                author=author.mention,
                rolls=", ".join(map(lambda x: str(x["roll"]), rolls)),
                skill_req=-skill_req,
            )

            if skill_check.group("FW"):
                FW = int(skill_check.group("FW"))
                FP = FW - skill_req
                response += "\n({FW} - {skill_req} = {FP} FP)".format(
                    FW=FW, skill_req=skill_req, FP=FP,
                )
                if FP < 0:
                    response += " QS: 0 FAIL"
                else:
                    response += " QS: {}".format(FP // 3 + 1)

            await send(response)

        debug_code = re.search(
            r"^debug:(?P<debugCommand>[a-z]*)$", msgstring, re.IGNORECASE
        )

        if debug_code:

            if debug_code.group("debugCommand") == "cache":
                response = "cache"

            if debug_code.group("debugCommand") == "fullCache":
                response = "fullCache"

            await send(response)


if __name__ == "__main__":
    persistence.init_db()
    client.run(TOKEN)
