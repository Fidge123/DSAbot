import re
import random
from typing import Optional

from discord import Message

from bot.response import Response
from bot.string_math import calc
from bot.stats import save_check


def parse(message: str) -> Optional[re.Match]:
    return re.search(
        r"""
            ^!?\ ?                                     # Optional exclamation mark
            (?P<amount>[0-9]*)[dw](?P<sides>[0-9]+)\ ? # <Number of dice> and <Number of sides> divided by "d" or "w"
            (?P<mod>(\ ?[\+\-]\ ?[0-9]+)*)\ ?          # A modifier (captured as `mod`)
            (?P<comment>.*?)$                          # Anything else is lazy-matched as a comment
        """,
        message,
        re.VERBOSE | re.I,
    )


def create_response(message: Message) -> Optional[Response]:
    regex_result = parse(message.content)
    if regex_result:
        die_amount = int(regex_result.group("amount") or 1)
        die_sides = int(regex_result.group("sides"))
        result_array = []
        aggregate = 0

        modifier = int(calc(regex_result.group("mod") or "0")[0])
        modifier_string = (" ({:+d})").format(modifier) if modifier != 0 else ""

        for _ in range(die_amount):
            roll = random.randint(1, die_sides)
            result_array.append(roll)
            aggregate += roll

        response = " {comment}\n{results}{modifier} = {FP}".format(
            comment=regex_result.group("comment").strip(),
            results=(" + ").join(str(x) for x in result_array),
            modifier=modifier_string,
            FP=aggregate + modifier,
        )

        save_check(message.author, "DiceRoll", result_array, die_sides)

        return Response(message.channel.send, message.author.mention + response)

    return None
