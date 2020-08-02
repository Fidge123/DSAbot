import re
import random


def parse(message):
    return re.search(
        r"""
            ^!?\ ?                        # Optional exclamation mark
            (?P<attr>(?:[0-9]+,?\ ?)+)\ ? # A non-zero amount of numbers divided by comma or space (captured as `attr`)
            (?:@\ ?(?P<FW>[0-9]+))?\ ?    # An @ followed by a number (captured as `FW`)
            (?:\+\ ?(?P<add>[0-9]+))?\ ?  # A + modifier (captured as `add`)
            (?:\-\ ?(?P<sub>[0-9]+))?\ ?  # A - modifier (captured as `sub`)
            (?P<comment>.*?)$             # Anything else is lazy-matched as a comment
        """,
        message,
        re.VERBOSE | re.IGNORECASE,
    )


def create_response(regex_result, author):
    if regex_result:
        # sanitize special characters and split into list of numbers
        attributes = (
            regex_result.group("attr")
            .strip()
            .replace(",", " ")
            .replace("  ", " ")
            .split(" ")
        )
        rolls = []
        add = int(regex_result.group("add") or 0)
        sub = int(regex_result.group("sub") or 0)

        for attr in attributes:
            rolls.append(
                {"attr": int(attr), "roll": random.randint(1, 20),}
            )

        skill_req = sum(
            map(lambda x: max([x["roll"] - x["attr"] - add + sub, 0]), rolls)
        )

        response = "{author} {comment}\n{rolls} ===> {skill_req}".format(
            author=author.mention,
            comment=regex_result.group("comment").strip(),
            rolls=", ".join(map(lambda x: str(x["roll"]), rolls)),
            skill_req=-skill_req,
        )

        if regex_result.group("FW"):
            FW = int(regex_result.group("FW"))
            FP = FW - skill_req
            response += "\n({FW} - {skill_req} = {FP} FP)".format(
                FW=FW, skill_req=skill_req, FP=FP,
            )
            if FP < 0:
                response += " QS: 0 FAIL"
            else:
                response += " QS: {}".format(max([FP - 1, 0]) // 3 + 1)

        if len(rolls) == 3 && list(map(lambda x: x["roll"], rolls)).count(1) >= 2:
            response += "\nKritischer Erfolg!"
        if len(rolls) == 3 && list(map(lambda x: x["roll"], rolls)).count(20) >= 2:
            response += "\nPatzer!"

        return response
