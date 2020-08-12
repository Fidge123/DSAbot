import re

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
    transform = {**GenericCheck.transform, "SR": lambda x: int(x)}
    _response = "{author} {comment}\n```py\nEEW:   {EAV}\nWürfel:{rolls}\nFW {SR:<4}{diffs} = {SP} FP\n{result}\n```"
    _routine = "{author} {comment}\n```py\nRoutineprobe: {SP} FP = QS {QL}\n```"

    @property
    def diffs(self):

        return [
            min([eav - roll, 0])
            for eav, roll in zip(self.data["EAV"], self.data["rolls"])
        ]

    @property
    def skill_points(self):
        return self.data["SR"] + sum(self.diffs)

    @property
    def routine(self):
        attr_ge_13 = all([attr >= 13 for attr in self.data["attributes"]])
        sr_ge_10 = self.data["SR"] >= 10 + 3 * -self.data["modifier"]
        return attr_ge_13 and sr_ge_10

    def ql(self, skill_points):
        return min([max([skill_points - 1, 0]) // 3 + 1, 6])

    def __str__(self):
        if self.routine:
            sp = self.data["SR"] - self.data["SR"] // 2  # Rounds up
            return self._routine.format(**self.data, SP=sp, QL=self.ql(sp))
        else:
            self.data["diffs"] = "".join("{:>4}".format(d or "") for d in self.diffs)
            self.data["SP"] = self.skill_points
            return super().__str__()

    def _get_result(self):
        if self.skill_points < 0 and self.data["rolls"].critical_success:
            return "Kritischer Erfolg! - Automatisch bestanden"
        if self.skill_points < 0 and self.data["rolls"].botch:
            return "Patzer!"
        if self.skill_points < 0:
            return "Nicht bestanden"
        if self.skill_points >= 0 and self.data["rolls"].botch:
            return "Patzer! - Automatisch nicht bestanden"
        if self.skill_points >= 0 and self.data["rolls"].critical_success:
            return "Kritischer Erfolg! (QS {})".format(self.ql(self.skill_points))
        else:
            return "Bestanden mit QS {}".format(self.ql(self.skill_points))
