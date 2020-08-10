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
        (?:@\ ?(?P<SR>[0-9]+))?\ ?        # An @ followed by a number (captured as `FW`)
        (?P<mod>(\ ?[\+\-]\ ?[0-9]+)*)\ ? # A modifier (captured as `mod`)
        (?P<comment>.*?)$                 # Anything else is lazy-matched as a comment
    """,
    re.VERBOSE | re.IGNORECASE,
)


class SkillCheck:
    critical_success = False
    botch = False
    has_quality_level = False

    res1 = "{author} {comment}\n{rolls} ===> {skill_req}{extra}"
    res2 = "{author} {comment}\n{rolls} ===> {skill_req}\n({SR} - {skill_req} = {SP} FP) {result}"

    def __init__(self, author, attr, skill_rating, mod, comment):
        self.author = author
        self.rolls = roll_for_attr(get_attributes(attr))
        self.skill_req = calc_skill_req(self.rolls, int(calc(mod or "0")))

        if skill_rating:
            self.has_quality_level = True
            self.skill_rating = int(skill_rating)
            self.skill_points = self.skill_rating - self.skill_req
            self.quality_level = max([self.skill_points - 1, 0]) // 3 + 1

        if len(self.rolls) == 3:
            self.critical_success = (
                list(map(lambda x: x["roll"], self.rolls)).count(1) >= 2
            )
            self.botch = list(map(lambda x: x["roll"], self.rolls)).count(20) >= 2

        self.comment = comment.strip()

    def result_string(self):
        if self.skill_points < 0 and self.critical_success:
            return "Automatisch bestanden\n**Kritischer Erfolg!**"
        if self.skill_points < 0 and self.botch:
            return "Nicht bestanden\n**Patzer!**"
        if self.skill_points < 0:
            return "Nicht bestanden"
        if self.skill_points >= 0 and self.botch:
            return "Automatisch nicht bestanden\n**Patzer!**"
        if self.skill_points >= 0 and self.critical_success:
            return "QS: {}\n**Kritischer Erfolg!**".format(self.quality_level)
        else:
            return "QS: {}".format(self.quality_level)

    def extra_string(self):
        if self.critical_success:
            return "\n**Kritischer Erfolg!**"
        if self.botch:
            return "\n**Patzer!**"
        else:
            return ""

    def __str__(self):
        if self.has_quality_level:
            return self.res2.format(
                author=self.author,
                comment=self.comment,
                rolls=rolls_to_str(self.rolls),
                skill_req=self.skill_req,
                SR=self.skill_rating,
                SP=self.skill_points,
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
            parsed.group("SR"),
            parsed.group("mod"),
            parsed.group("comment"),
        )
    else:
        return
