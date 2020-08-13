import re

from bot import note
from bot.checks import SkillCheck, GenericCheck, AttributeCheck

lastCheck = {}
fate_regex = re.compile(
    r"^(schips?|fate)\ (?P<reroll>((r|reroll\ ?)|(k|keep\ ?))+)$", re.IGNORECASE
)
retry_regex = re.compile(r"retry", re.IGNORECASE)
repeat_regex = re.compile(r"repeat", re.IGNORECASE)
force_regex = re.compile(r"force", re.IGNORECASE)


def create_check(msg, author):
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


def schip_split(input):
    words = input.split()
    if len(words) == 1:
        return [letter == "r" for letter in input]
    else:
        return [word.lower() == "reroll" for word in words]


def create_response(msg, author):
    check = create_check(msg, author)

    if check:
        lastCheck[hash(author)] = check
        return str(check)

    if hash(author) in lastCheck:
        match = fate_regex.search(msg)
        if match:
            note_id = "schips_{}".format(str(author))
            check = lastCheck[hash(author)]

            if check.data["rolls"].botch:
                return "{} Einsatz von Schips nicht erlaubt".format(author.mention)
            if note_id not in note.number_notes:
                note.create_note(note_id, 3, author)
            if note.number_notes[note_id] <= 0:
                return "{} Keine Schips übrig!".format(author.mention)
            note.create_note(note_id, -1, author)

            for i, schip in enumerate(schip_split(match.group("reroll"))):
                if schip:
                    check.data["rolls"].reroll(i)
            return str(check)

        match = retry_regex.search(msg)
        if match:
            check = lastCheck[hash(author)]
            check.data["modifier"] -= 1
            check.recalculate()
            return str(check)

        match = repeat_regex.search(msg)
        if match:
            check = lastCheck[hash(author)]
            check.recalculate()
            return str(check)

        match = force_regex.search(msg)
        if match:
            check = lastCheck[hash(author)]
            check.force()
            return str(check)