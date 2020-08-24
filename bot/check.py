import re
from typing import Dict, List, Optional, Tuple

from discord import Message, Member, Embed

from bot import note
from bot.checks import SkillCheck, GenericCheck, AttributeCheck, CumulativeCheck

lastCheck: Dict[int, GenericCheck] = {}
fate_regex = re.compile(
    r"^(schips?|fate)\ (?P<reroll>((r|reroll\ ?)|(k|keep\ ?))+)$", re.IGNORECASE
)
retry_regex = re.compile(r"retry", re.IGNORECASE)
repeat_regex = re.compile(r"repeat", re.IGNORECASE)
force_regex = re.compile(r"force", re.IGNORECASE)


def create_check(msg: str, author: Member) -> Optional[GenericCheck]:
    try:
        return CumulativeCheck(msg, author)
    except ValueError:
        pass

    try:
        return SkillCheck(msg, author)
    except ValueError:
        pass

    try:
        return AttributeCheck(msg, author)
    except ValueError:
        pass

    try:
        return GenericCheck(msg, author)
    except ValueError:
        pass

    return None


def schip_split(input_string: str) -> List[bool]:
    input_string = re.sub(r"reroll\ ?", "r", input_string, re.IGNORECASE)
    input_string = re.sub(r"keep\ ?", "k", input_string, re.IGNORECASE)
    return [letter == "r" for letter in input_string]


def create_response(content: str, message: Message) -> Optional[Tuple[str, Embed]]:
    author = message.author
    check = create_check(content, author)

    if check:
        lastCheck[hash(author)] = check
        return str(check), None

    if hash(author) in lastCheck:
        match = fate_regex.search(content)
        if match:
            note_id = "schips_{}".format(str(author))
            n = note.get_note(note_id, author.guild.id)
            check = lastCheck[hash(author)]

            if check.data["rolls"].botch:
                return author.mention + " Einsatz von Schips nicht erlaubt", None
            if isinstance(check, CumulativeCheck):
                return (
                    author.mention
                    + " Einsatz von Schips bei Sammelproben (bisher) nicht unterstützt",
                    None,
                )
            if not n:
                n = note.create_note(note_id, 3, author)
            if n.value == 0:
                return "{} Keine Schips übrig!".format(author.mention), None
            note.create_note(note_id, -1, author)

            for i, schip in enumerate(schip_split(match.group("reroll"))):
                if schip:
                    check.data["rolls"].reroll(i)
            return str(check), None

        match = retry_regex.search(content)
        if match:
            check = lastCheck[hash(author)]
            if isinstance(check, CumulativeCheck):
                check._initial_mod -= 1
            else:
                check.data["modifier"] -= 1
            check.recalculate()
            return str(check), None

        match = repeat_regex.search(content)
        if match:
            check = lastCheck[hash(author)]
            check.recalculate()
            return str(check), None

        match = force_regex.search(content)
        if match:
            check = lastCheck[hash(author)]
            if isinstance(check, SkillCheck):
                check.force()
                return str(check), None
    return None
