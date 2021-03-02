import re
from typing import Optional

from discord import Message, Member

from bot import note
from bot.response import Response
from bot.checks import SkillCheck, GenericCheck, AttributeCheck, CumulativeCheck

lastCheck: dict[int, GenericCheck] = {}
fate_regex = re.compile(
    r"^(s?chips?|fate)\ (?P<reroll>((r|reroll\ ?)|(k|keep\ ?))+)$", re.I
)
aptitude_regex = re.compile(r"^(begabung|aptitude)\ (?P<reroll>[1-3])$", re.I)
retry_regex = re.compile(r"retry", re.I)
repeat_regex = re.compile(r"repeat", re.I)
force_regex = re.compile(r"force", re.I)


def create_check(content: str) -> Optional[GenericCheck]:
    for Check in [CumulativeCheck, SkillCheck, AttributeCheck, GenericCheck]:
        try:
            return Check(content)
        except ValueError:
            pass

    return None


def handle_fate(content: str, author: Member) -> Optional[str]:
    match = fate_regex.search(content)
    if not match:
        return None

    note_id = "schips_{}".format(str(author))
    n = note.get_note(note_id, author.guild.id)
    check = lastCheck[hash(author)]

    if check.data["rolls"].botch:
        return " Einsatz von Schips nicht erlaubt"
    if isinstance(check, CumulativeCheck):
        return " Einsatz von Schips bei Sammelproben (bisher) nicht unterstützt"
    if not n:
        n = note.create_note(note_id, True, 3, author)
    if n.value == 0:
        return " Keine Schips übrig!"
    note.create_note(note_id, False, -1, author)

    for i, schip in enumerate(schip_split(match.group("reroll"))):
        if schip:
            check.data["rolls"].reroll(i)
    return str(check)


def handle_aptitude(content: str, author: Member) -> Optional[str]:
    match = aptitude_regex.search(content)
    if not match:
        return None

    check = lastCheck[hash(author)]

    if check.data["rolls"].botch:
        return " Einsatz von Begabung nicht erlaubt"
    if isinstance(check, CumulativeCheck):
        return " Einsatz von Begabung bei Sammelproben (bisher) nicht unterstützt"

    check.data["rolls"].reroll(int(match.group("reroll")) - 1, True)

    return str(check)


def handle_retry(content: str, author: Member) -> Optional[str]:
    match = retry_regex.search(content)
    if not match:
        return None

    check = lastCheck[hash(author)]
    if isinstance(check, CumulativeCheck):
        check._initial_mod -= 1
    else:
        check.data["modifier"] -= 1
    check.recalculate()
    return str(check)


def handle_repeat(content: str, author: Member) -> Optional[str]:
    match = repeat_regex.search(content)
    if not match:
        return None
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
    return None


def schip_split(input_string: str) -> list[bool]:
    input_string = re.sub(r"reroll\ ?", "r", input_string, re.I)
    input_string = re.sub(r"keep\ ?", "k", input_string, re.I)
    return [letter == "r" for letter in input_string]


def create_response(message: Message) -> Optional[Response]:
    author = message.author
    content = message.content
    check = create_check(content)

    if check:
        lastCheck[hash(author)] = check
        return Response(message.channel.send, author.mention + str(check))

    if hash(author) in lastCheck:
        for handle in [
            handle_fate,
            handle_aptitude,
            handle_retry,
            handle_repeat,
            handle_force,
        ]:
            response = handle(content, author)
            if response:
                return Response(message.channel.send, author.mention + response)

    return None
