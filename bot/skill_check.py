import re
from bot.string_math import calc

from bot.skill_check_helper import (
    get_attributes,
    roll_for_attr,
    calc_skill_req,
    rolls_to_str,
)


matcher = re.compile(
    r"""
        ^!?\ ?                            # Optional exclamation mark
        (?P<attr>(?:[0-9]+,?\ ?)+)\ ?     # A non-zero amount of numbers divided by comma or space (captured as `attr`)
        (?:@\ ?(?P<FW>[0-9]+))?\ ?        # An @ followed by a number (captured as `FW`)
        (?P<mod>(\ ?[\+\-]\ ?[0-9]+)*)\ ? # A modifier (captured as `mod`)
        (?P<comment>.*?)$                 # Anything else is lazy-matched as a comment
    """,
    re.VERBOSE | re.IGNORECASE,
)


class SkillCheck:
    crit = False
    fail = False
    hasQS = False

    def __init__(self, author, attr, FW, mod, comment):
        self.author = author
        self.rolls = roll_for_attr(get_attributes(attr))
        self.skill_req = calc_skill_req(self.rolls, calc(mod or "0"))

        if FW:
            self.hasQS = True
            self.FW = int(FW)
            self.FP = self.FW - self.skill_req
            self.QS = max([self.FP - 1, 0]) // 3 + 1

        if len(self.rolls) == 3:
            self.crit = list(map(lambda x: x["roll"], self.rolls)).count(1) >= 2
            self.fail = list(map(lambda x: x["roll"], self.rolls)).count(20) >= 2

        self.comment = comment.strip()

    def __str__(self):
        response = "{author} {comment}\n{rolls} ===> {skill_req}".format(
            author=self.author,
            comment=self.comment,
            rolls=rolls_to_str(self.rolls),
            skill_req=-self.skill_req,
        )

        if self.hasQS:
            response += "\n({FW} - {skill_req} = {FP} FP)".format(
                FW=self.FW, skill_req=self.skill_req, FP=self.FP
            )
            if self.FP < 0:
                if self.crit:
                    response += " Automatisch bestanden"
                else:
                    response += " Nicht bestanden"
            else:
                if self.fail:
                    response += " Automatisch nicht bestanden"
                else:
                    response += " QS: {}".format(self.QS)

        if self.crit:
            response += "\n**Kritischer Erfolg!**"
        if self.fail:
            response += "\n**Patzer!**"

        return response


def create_skill_check(message, author):
    parsed = matcher.search(message)
    if parsed:
        return SkillCheck(
            author.mention,
            parsed.group("attr"),
            parsed.group("FW"),
            parsed.group("mod"),
            parsed.group("comment"),
        )
    else:
        return
