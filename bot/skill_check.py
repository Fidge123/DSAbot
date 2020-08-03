import re

from bot.skill_check_helper import (
    get_attributes,
    roll_for_attr,
    calc_skill_req,
    rolls_to_str,
)


def is_skill_check(message):
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


def create_response(parsed, author):
    if parsed:
        rolls = roll_for_attr(get_attributes(parsed.group("attr")))
        skill_req = calc_skill_req(rolls, parsed.group("add"), parsed.group("sub"))

        response = "{author} {comment}\n{rolls} ===> {skill_req}".format(
            author=author.mention,
            comment=parsed.group("comment").strip(),
            rolls=rolls_to_str(rolls),
            skill_req=-skill_req,
        )

        crit = len(rolls) == 3 and list(map(lambda x: x["roll"], rolls)).count(1) >= 2
        fail = len(rolls) == 3 and list(map(lambda x: x["roll"], rolls)).count(20) >= 2

        if parsed.group("FW"):
            FW = int(parsed.group("FW"))
            FP = FW - skill_req
            QS = max([FP - 1, 0]) // 3 + 1
            response += "\n({FW} - {skill_req} = {FP} FP)".format(
                FW=FW, skill_req=skill_req, FP=FP
            )
            if FP < 0:
                if crit:
                    response += " Automatisch bestanden"
                else:
                    response += " Nicht bestanden"
            else:
                if fail:
                    response += " Automatisch nicht bestanden"
                else:
                    response += " QS: {}".format(QS)

        if crit:
            response += "\n**Kritischer Erfolg!**"
        if fail:
            response += "\n**Patzer!**"

        return response
