import re

from bot import persistence

number_notes = {}


def on_load():
    notes = persistence.load_notes()
    for (id, value) in notes:
        number_notes[id] = value


def notes_to_str():
    lk = max(map(len, number_notes.keys()))
    lv = max(map(lambda x: len(str(x)), number_notes.values()))
    return "\n".join([f"{k:<{lk}}: {v:>{lv}}" for k, v in number_notes.items()])


def create_note(note_id, value, user):
    if note_id not in number_notes:
        number_notes[note_id] = 0

    number_notes[note_id] += int(value)
    response = "{user} {note_id} is now {value}".format(
        user=user.mention, note_id=note_id, value=number_notes[note_id],
    )
    persistence.persist_note(note_id, number_notes[note_id])
    return response


def get_notes(user):
    if len(number_notes.items()):
        return "{user}\n```{notes}```".format(user=user.mention, notes=notes_to_str())
    else:
        return "{} Es gibt keine Notizen.".format(user.mention)


def create_response(message, user):
    create_match = re.search(
        r"^note:(?P<id>\w+)(->(?P<number>[\+\-]?[0-9]+))?$", message, re.IGNORECASE,
    )
    if create_match:
        return create_note(create_match.group("id"), create_match.group("number"), user)

    get_match = re.search(r"^notes$", message, re.IGNORECASE)
    if get_match:
        return get_notes(user)
