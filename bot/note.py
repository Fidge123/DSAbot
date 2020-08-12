import re

from bot import persistence

number_notes = {}


def on_load():
    notes = persistence.load_notes()
    for (id, value, user) in notes:
        if user not in number_notes:
            number_notes[user] = {}

        number_notes[user][id] = value


def notes_to_str(user_hash):
    lk = max(map(len, number_notes[user_hash].keys()))
    lv = max(map(lambda x: len(str(x)), number_notes[user_hash].values()))
    return "\n".join(
        [f"{k:<{lk}}: {v:>{lv}}" for k, v in number_notes[user_hash].items()]
    )


def create_note(note_id, value, user):
    user_hash = str(hash(user))
    if user_hash not in number_notes:
        number_notes[user_hash] = {}

    if note_id not in number_notes[user_hash]:
        number_notes[user_hash][note_id] = 0

    number_notes[user_hash][note_id] += int(value)
    response = "{user} {note_id} is now {value}".format(
        user=user.mention, note_id=note_id, value=number_notes[user_hash][note_id],
    )
    persistence.persist_note(
        note_id, number_notes[user_hash][note_id], user_hash,
    )
    return response


def get_notes(user):
    user_hash = str(hash(user))

    if user_hash in number_notes:
        return "{user}\n```{notes}```".format(
            user=user.mention, notes=notes_to_str(user_hash)
        )
    else:
        return "{} Du hast keine Notizen.".format(user.mention)


def create_response(message, user):
    create_match = re.search(
        r"^note:(?P<id>\w+)(->(?P<number>[\+\-]?[0-9]+))?$", message, re.IGNORECASE,
    )
    if create_match:
        return create_note(create_match.group("id"), create_match.group("number"), user)

    get_match = re.search(r"^notes$", message, re.IGNORECASE)
    if get_match:
        return get_notes(user)
