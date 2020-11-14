import re
from typing import Dict, Any
from bot.checks.skill_check import SkillCheck


class CumulativeCheck(SkillCheck):
    matcher = re.compile(
        r"""
            ^!?\ ?                                # Optional exclamation mark
            (?P<force>f(?:orce)?\ )?              # Check if force
            S(ammelprobe)?\ ?                     # Prefix S or Sammelprobe
            (?P<tries>[0-9]+)\ ?[x\*\ ]\ ?        # Number of allowed tries
            (?P<time>[0-9]+)\ ?(?P<unit>\w+)\ ?   # Time per round
            (?P<attributes>(?:[0-9]+,?\ ?){3})\ ? # A non-zero amount of numbers divided by comma or space
            (?:@\ ?(?P<SR>[0-9]+))\ ?             # An @ followed by a number
            (?P<modifier>(\ *[\+\-]\ *[0-9]+)*)   # A modifier
            (\ (?P<comment>.*?))?$                # Anything else is lazy-matched as a comment
        """,
        re.VERBOSE | re.I,
    )
    transform: Dict[str, Any] = {
        **SkillCheck.transform,
        "tries": int,
        "time": int,
        "unit": str,
    }
    _response = "EEW{EAV}  Würfel{rolls}  FW{SR}{diffs}={SP:>2}FP  {result}"
    _routine = "Routineprobe {SP} FP = QS {QL}"
    _impossible = "Probe nicht möglich  EEW{EAV}"

    @property
    def routine(self) -> bool:
        return False

    def recalculate(self) -> None:
        self.round = 0
        self.total_ql = 0
        if hasattr(self, "_initial_mod"):
            self.data["modifier"] = self._initial_mod
        super().recalculate()

    def __init__(self, message: str):
        super().__init__(message)
        self._initial_mod = self.data["modifier"]

    def __str__(self) -> str:
        response = " {comment}\n```py".format(**self.data)
        while (
            self.total_ql < 10
            and self.round < self.data["tries"]
            and self.total_ql >= 0  # No Botch
        ):
            self.round += 1
            response += "\nRunde {:>2}: {}".format(self.round, super().__str__())
            super().recalculate()

        if self.total_ql < 6:
            response += "\n\nProbe fehlgeschlagen"
        elif self.total_ql < 10:
            response += "\n\nTeilerfolg"
        else:
            response += "\n\nProbe erfolgreich"

        return "{} nach {} Runden ({})\n```".format(
            response,
            self.round,
            str(self.data["time"] * self.round) + self.data["unit"],
        )

    def _get_result(self) -> str:
        if self.data["rolls"].critical_success:
            self.total_ql += self.ql(self.skill_points) * 2
            self.data["modifier"] = self._initial_mod
            return "Kritischer Erfolg! (QS{})".format(self.ql(self.skill_points) * 2)
        if self.data["rolls"].botch:
            self.total_ql = -1
            return "Patzer!"
        if self.skill_points < 0:
            self.data["modifier"] -= 1
            return "Nicht bestanden"
        else:
            self.total_ql += self.ql(self.skill_points)
            return "QS{}".format(self.ql(self.skill_points))
