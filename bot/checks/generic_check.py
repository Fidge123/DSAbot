import re

from bot.string_math import calc
from bot.checks.check_roll import CheckRolls
from bot.checks.attributes import Attributes


class GenericCheck:
    matcher = re.compile(
        r"""
            ^!?\ ?                              # Optional exclamation mark
            (?P<attributes>(?:[0-9]+,?\ ?)+)\ ? # A non-zero amount of numbers divided by comma or space
            (?P<modifier>(\ *[\+\-]\ *[0-9]+)*) # A modifier
            (\ (?P<comment>.*?))?$              # Anything else is lazy-matched as a comment
        """,
        re.VERBOSE | re.IGNORECASE,
    )
    transform = {
        "attributes": lambda x: Attributes(
            [int(attr) for attr in re.split(r"[, ]+", x.strip(", "))]
        ),
        "modifier": lambda x: int(calc(x or "0")),
        "comment": lambda x: (x or "").strip(),
    }
    _response = "{author} {comment}\n```py\nEEW:   {EAV}\nWürfel:{rolls}\n{result}\n```"
    _impossible = "{author} {comment}\n```py\nEEW:{EAV}\nProbe nicht möglich\n```"

    def __init__(self, message, author):
        parsed = self.matcher.search(message)
        if parsed:
            self.data = {}
            for name, value in parsed.groupdict().items():
                self.data[name] = self.transform[name](value)
            self.data["author"] = author.mention
            self.recalculate()
        else:
            raise ValueError

    def recalculate(self):
        self.data["EAV"] = Attributes(
            [attr + self.data["modifier"] for attr in self.data["attributes"]]
        )
        self.data["rolls"] = CheckRolls(len(self.data["attributes"]))

    def __str__(self):
        if self.impossible:
            return self._impossible.format(**self.data)
        return self._response.format(**self.data, result=self._get_result(),)

    @property
    def impossible(self):
        return any(eav <= 0 for eav in self.data["EAV"])

    def _get_result(self):
        rolls: CheckRolls = self.data["rolls"]
        if rolls.critical_success:
            return "Kritischer Erfolg!"
        if rolls.botch:
            return "Patzer!"
        if all(roll <= eav for roll, eav in zip(rolls, self.data["EAV"])):
            return "Bestanden"
        else:
            return "Nicht bestanden"
