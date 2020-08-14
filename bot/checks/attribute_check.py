import re

from bot.checks.generic_check import GenericCheck


class AttributeCheck(GenericCheck):
    matcher = re.compile(
        r"""
            ^!?\ ?                              # Optional exclamation mark
            (?P<attributes>[0-9]+)\ ?           # A non-zero amount of numbers divided by comma or space
            (?P<modifier>(\ *[\+\-]\ *[0-9]+)*) # A modifier
            (\ (?P<comment>.*?))?$              # Anything else is lazy-matched as a comment
        """,
        re.VERBOSE | re.IGNORECASE,
    )

    def _get_result(self) -> str:
        rolls = self.data["rolls"]
        if rolls.critical_success and rolls.confirmation_roll <= self.data["EAV"][0]:
            return "Kritischer Erfolg!"
        if rolls.critical_success:
            return "Unbestätigter kritischer Erfolg"
        if rolls.botch and rolls.confirmation_roll > self.data["EAV"][0]:
            return "Patzer!"
        if rolls.botch:
            return "Unbestätigter Patzer"
        if all(roll <= eav for roll, eav in zip(rolls, self.data["EAV"])):
            return "Bestanden"
        else:
            return "Nicht bestanden"
