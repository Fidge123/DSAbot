import re
import random


def parse(message):
    return re.search(
        r"""
            ^!?\ ?                                     # Optional exclamation mark
            (?P<amount>[0-9]*)[dw](?P<sides>[0-9]+)\ ? # <Number of dice> and <Number of sides> divided by "d" or "w"
            (?:\+\ ?(?P<add>[0-9]+))?\ ?               # A + modifier (captured as `add`)
            (?:\-\ ?(?P<sub>[0-9]+))?\ ?               # A - modifier (captured as `sub`)
            (?P<comment>.*?)$                          # Anything else is lazy-matched as a comment
        """,
        message,
        re.VERBOSE | re.IGNORECASE,
    )


def create_response(regex_result, author):
    if regex_result:
        die_amount = int(regex_result.group("amount") or 1)
        die_sides = int(regex_result.group("sides"))
        result_array = []
        aggregate = 0

        add = int(regex_result.group("add") or 0)
        sub = int(regex_result.group("sub") or 0)
        modifier_string = (" ({:+d})").format(add - sub) if add - sub != 0 else ""

        for _ in range(die_amount):
            roll = random.randint(1, die_sides)
            result_array.append(str(roll))
            aggregate += roll

        return "{author} {comment}\n{results}{modifier} = {FP}".format(
            author=author.mention,
            comment=regex_result.group("comment").strip(),
            results=(" + ").join(result_array),
            modifier=modifier_string,
            FP=aggregate + add - sub,
        )
