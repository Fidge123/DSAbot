import re
import random

from bot.string_math import calc


class CheckRolls:
    def __init__(self, num):
        self.rolls = []
        for _ in range(num):
            self.rolls.append(random.randint(1, 20))

    @property
    def critical_success(self):
        return len(self) == 3 and self.rolls.count(1) >= 2

    @property
    def botch(self):
        return len(self) == 3 and self.rolls.count(20) >= 2

    def __len__(self):
        return len(self.rolls)

    def __getitem__(self, key):
        return self.rolls[key]

    def __str__(self):
        return ", ".join(str(roll) for roll in self.rolls)

    def __format__(self, spec):
        if spec in ["", "s"]:
            return str(self)
        else:
            raise TypeError


class GenericCheck:
    matcher = re.compile(
        r"""
            ^!?\ ?                                 # Optional exclamation mark
            (?P<attributes>(?:[0-9]+,?\ ?)+)\ ?    # A non-zero amount of numbers divided by comma or space
            (?P<modifier>(\ *[\+\-]\ *[0-9]+)*)\ ? # A modifier
            (?P<comment>.*?)$                      # Anything else is lazy-matched as a comment
        """,
        re.VERBOSE | re.IGNORECASE,
    )
    transform = {
        "attributes": lambda x: [int(attr) for attr in re.split(r"[, ]+", x.strip())],
        "modifier": lambda x: int(calc(x or "0")),
        "comment": lambda x: x.strip(),
    }
    _response = "{author} {comment}\n{rolls} ===> {skill_req}{result}"

    def __init__(self, message, author):
        parsed = self.matcher.search(message)
        if parsed:
            self.data = {}
            for name, value in parsed.groupdict().items():
                self.data[name] = self.transform[name](value)
            self.data["author"] = author.mention

            self.data["rolls"] = CheckRolls(len(self.data["attributes"]))
            self.data["skill_req"] = self._skill_req()
        else:
            raise ValueError

    def __str__(self):
        return self._response.format(**self.data, result=self._get_result(),)

    def _skill_req(self):
        skill_req = 0
        for attr, roll in zip(self.data["attributes"], self.data["rolls"]):
            skill_req += max([roll - (attr + self.data["modifier"]), 0])
        return skill_req

    def _get_result(self):
        if self.data["rolls"].critical_success:
            return "\n**Kritischer Erfolg!**"
        if self.data["rolls"].botch:
            return "\n**Patzer!**"
        else:
            return ""
