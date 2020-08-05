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

    res1 = "{author} {comment}\n{rolls} ===> {skill_req}{extra}"
    res2 = "{author} {comment}\n{rolls} ===> {skill_req_n}\n({FW} - {skill_req} = {FP} FP) {result}"

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

    def result_string(self):
        if self.FP < 0 and self.crit:
            return "Automatisch bestanden\n**Kritischer Erfolg!**"
        if self.FP < 0 and self.fail:
            return "Nicht bestanden\n**Patzer!**"
        if self.FP < 0:
            return "Nicht bestanden"
        if self.FP >= 0 and self.fail:
            return "Automatisch nicht bestanden\n**Patzer!**"
        if self.FP >= 0 and self.crit:
            return "QS: {}\n**Kritischer Erfolg!**".format(self.QS)
        else:
            return "QS: {}".format(self.QS)

    def extra_string(self):
        if self.crit:
            return "\n**Kritischer Erfolg!**"
        if self.fail:
            return "\n**Patzer!**"
        else:
            return ""

    def __str__(self):
        if self.hasQS:
            return self.res2.format(
                author=self.author,
                comment=self.comment,
                rolls=rolls_to_str(self.rolls),
                skill_req=self.skill_req,
                skill_req_n=-self.skill_req,
                FW=self.FW,
                FP=self.FP,
                result=self.result_string(),
            )

        else:
            return self.res1.format(
                author=self.author,
                comment=self.comment,
                rolls=rolls_to_str(self.rolls),
                skill_req=-self.skill_req,
                extra=self.extra_string(),
            )


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
