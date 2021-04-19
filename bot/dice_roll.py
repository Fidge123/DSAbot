import re
from typing import Optional

from discord import Message

from bot.response import Response
from bot.string_math import calc
from bot.stats import save_check


def parse(message: str) -> Optional[re.Match]:
    return re.search(
        r"""
            ^!?\ ?                                # Optional exclamation mark
            (?P<calc>([0-9\+\-\*\/\(\)dw\ ]+))\ ? # The calculation string captured as `calc`
            (?P<comment>.*?)$                     # Anything else is lazy-matched as a comment
        """,
        message,
        re.VERBOSE | re.I,
    )


def create_response(message: Message) -> Optional[Response]:
    regex_result = parse(message.content)
    if regex_result:
        try:
            result, rolls = calc(regex_result.group("calc") or "0")

            response = " {comment}\n[{results}]\nErgebnis: **{FP}**".format(
                comment=regex_result.group("comment").strip(),
                results=("] [").join(
                    [
                        " + ".join([str(roll) for roll in roll_list])
                        for sides, roll_list in rolls
                    ]
                ),
                FP=int(result),
            )

            for sides, roll_list in rolls:
                save_check(
                    message.author,
                    "DiceRoll",
                    [int(roll) for roll in roll_list],
                    sides,
                )

            return Response(message.channel.send, message.author.mention + response)
        except:
            return None

    return None
