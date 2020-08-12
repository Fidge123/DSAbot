import re

from bot.string_math import calc
from bot.checks.generic_check import GenericCheck


class SkillCheck(GenericCheck):
    matcher = re.compile(
        r"""
            ^!?\ ?                                 # Optional exclamation mark
            (?P<attributes>(?:[0-9]+,?\ ?){3})\ ?  # A non-zero amount of numbers divided by comma or space
            (?:@\ ?(?P<SR>[0-9]+))\ ?              # An @ followed by a number
            (?P<modifier>(\ *[\+\-]\ *[0-9]+)*)\ ? # A modifier
            (?P<comment>.*?)$                      # Anything else is lazy-matched as a comment
        """,
        re.VERBOSE | re.IGNORECASE,
    )
    transform = {
        "attributes": lambda x: [int(a) for a in re.split(r"[, ]+", x.strip(", "))],
        "SR": lambda x: int(x),
        "modifier": lambda x: int(calc(x or "0")),
        "comment": lambda x: x.strip(),
    }
    _response = "{author} {comment}\n{rolls} ===> {skill_req}\n({SR} - {skill_req} = {SP} FP) {result}"

    @property
    def skill_points(self):
        return self.data["SR"] - self.data["skill_req"]

    @property
    def quality_level(self):
        return min([max([self.skill_points - 1, 0]) // 3 + 1, 6])

    def __str__(self):
        return self._response.format(
            **self.data, SP=self.skill_points, result=self._get_result(),
        )

    def _get_result(self):
        if self.skill_points < 0 and self.data["rolls"].critical_success:
            return "Automatisch bestanden\n**Kritischer Erfolg!**"
        if self.skill_points < 0 and self.data["rolls"].botch:
            return "Nicht bestanden\n**Patzer!**"
        if self.skill_points < 0:
            return "Nicht bestanden"
        if self.skill_points >= 0 and self.data["rolls"].botch:
            return "Automatisch nicht bestanden\n**Patzer!**"
        if self.skill_points >= 0 and self.data["rolls"].critical_success:
            return "QS: {}\n**Kritischer Erfolg!**".format(self.quality_level)
        else:
            return "QS: {}".format(self.quality_level)
