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


def create_check(msg: str, mention: str) -> Optional[GenericCheck]:
    try:
        return CumulativeCheck(msg, mention)
    except ValueError:
        pass

    try:
        return SkillCheck(msg, mention)
    except ValueError:
        pass

    try:
        return AttributeCheck(msg, mention)
    except ValueError:
        pass

    try:
        return GenericCheck(msg, mention)
    except ValueError:
        pass

    return None


def handle_fate(content: str, author: Member) -> Optional[str]:
    match = fate_regex.search(content)
    mention = author.mention
    if match:
        note_id = "schips_{}".format(str(author))
        n = note.get_note(note_id, author.guild.id)
        check = lastCheck[hash(author)]

        if check.data["rolls"].botch:
            return f"{mention} Einsatz von Schips nicht erlaubt"
        if isinstance(check, CumulativeCheck):
            return f"{mention} Einsatz von Schips bei Sammelproben (bisher) nicht unterstützt"
        if not n:
            n = note.create_note(note_id, 3, author)
        if n.value == 0:
            return f"{mention} Keine Schips übrig!"
        note.create_note(note_id, -1, author)

        for i, schip in enumerate(schip_split(match.group("reroll"))):
            if schip:
                check.data["rolls"].reroll(i)
        return str(check)


def handle_retry(content: str, author: Member) -> Optional[str]:
    match = retry_regex.search(content)
    if match:
        check = lastCheck[hash(author)]
        if isinstance(check, CumulativeCheck):
            check._initial_mod -= 1
        else:
            check.data["modifier"] -= 1
        check.recalculate()
        return str(check)


def handle_repeat(content: str, author: Member) -> Optional[str]:
    match = repeat_regex.search(content)
    if match:
        check = lastCheck[hash(author)]
        check.recalculate()
        return str(check)


def handle_force(content: str, author: Member) -> Optional[str]:
    match = force_regex.search(content)
    if match:
        check = lastCheck[hash(author)]
        if isinstance(check, SkillCheck):
            check.force()
            return str(check)


def schip_split(input_string: str) -> List[bool]:
    input_string = re.sub(r"reroll\ ?", "r", input_string, re.IGNORECASE)
    input_string = re.sub(r"keep\ ?", "k", input_string, re.IGNORECASE)
    return [letter == "r" for letter in input_string]


def create_response(message: Message) -> Optional[Tuple[str, Embed]]:
    author = message.author
    content = message.content
    check = create_check(content, author.mention)

    if check:
        lastCheck[hash(author)] = check
        return str(check), None

    if hash(author) in lastCheck:
        for handle in [handle_fate, handle_retry, handle_repeat, handle_force]:
            response = handle(content, author)
            if response:
                return response, None

    return None
