import discord
from dotenv import load_dotenv
import os
import user
import re
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
permittedChannels = []
userCharacters = {}
verbose = False


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

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
                await send("I am listening for rolls here")
            else:
                await send("I am already listening")

    if channel in permittedChannels:


        if "BEGONE" in msgstring:
            if channel in permittedChannels:
                permittedChannels.remove(channel)
                await send("I have left")

        if "DIE" in msgstring:
            await message.add_reaction("\U0001f480")
            await send("I shall die.")
            await client.close()
            return

        if re.search("^!*[0-9]+(D|d|w|W)[0-9]+$", msgstring):
            diestring = msgstring
            diestring.upper()
            if "W" in diestring:
                diesplit = diestring.split("W")
            else:
                diesplit = diestring.split("D")

            response = author.mention + "\n"

            for dieammount in range(int(diesplit[0])):
                roll = random.randint(1, int(diesplit[1]))
                response = response + str(roll) + ", "
            
            response = response[:-2]

            await send(response)

        if re.search("^([0-9]+,\ *)*[0-9]+$", msgstring):
            diestring = msgstring
            diestring.replace(" ", "")
            diesplit = msgstring.split(",")

            response = author.mention + "\n"
            skillReq = 0

            for attr in diesplit:
                roll = random.randint(1, 20)
                result = roll - int(attr)

                if result < 0: result = 0

                response += str(roll) + ", "
                skillReq += result

            response = response[:-2]
            response += "===> " + str(skillReq)
            await send(response)

        if re.search("([0-9]+,\ *)*[0-9]+@[0-9]+$", msgstring):
            diestring = msgstring
            diestring.replace(" ", "")
            skillSplit = diestring.split("@")
            skillLevel = int(skillSplit[1])
            diesplit = skillSplit[0].split(",")

            response = author.mention + "\n"
            skillReq = 0

            for attr in diesplit:
                roll = random.randint(1, 20)
                result = roll - int(attr)

                if result < 0: result = 0

                response += str(roll) + ", "
                skillReq += result

            remainder = skillLevel - skillReq

            response = response[:-2]
            response += " ===> " + str(skillReq)

            if remainder < 0:
                response += "\nQS: 0 FAIL"
            else:
                response += "\nQS: " + str(remainder//3 + 1)

            await send(response)

client.run(TOKEN)