import re

from bot import persistence

number_notes = {}


def on_load():
    notes = persistence.load_notes()
    for (id, value, user) in notes:
        if user not in number_notes:
            number_notes[user] = {}

        number_notes[user][id] = value


def create(message):
    return re.search(
        r"^note:(?P<id>\w+)(->(?P<number>[\+\-]?[0-9]+))?$", message, re.IGNORECASE,
    )


def get(message):
    return re.search(r"^notes$", message, re.IGNORECASE)


def notes_to_str(user_hash):
    lk = max(map(len, number_notes[user_hash].keys()))
    lv = max(map(lambda x: len(str(x)), number_notes[user_hash].values()))
    return "\n".join(
        [f"{k:<{lk}}: {v:>{lv}}" for k, v in number_notes[user_hash].items()]
    )


def create_response(message, user):
    create_note = create(message)
    user_hash = str(hash(user))
    if create_note:
        if user_hash not in number_notes:
            number_notes[user_hash] = {}

        if create_note.group("id") not in number_notes[user_hash]:
            number_notes[user_hash][create_note.group("id")] = 0

        number_notes[user_hash][create_note.group("id")] += int(
            create_note.group("number")
        )
        response = "{} is now {}".format(
            create_note.group("id"), number_notes[user_hash][create_note.group("id")]
        )
        persistence.persist_note(
            create_note.group("id"),
            number_notes[user_hash][create_note.group("id")],
            user_hash,
        )
        return response

    get_notes = get(message)
    if get_notes:
        if user_hash in number_notes:
            return "```{}```".format(notes_to_str(user_hash))
        else:
            return "Du hast keine Notizen."
