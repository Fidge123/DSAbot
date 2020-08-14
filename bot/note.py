import re
from typing import Dict

import discord

from bot import persistence

number_notes: Dict[str, int] = {}


def on_load() -> None:
    notes = persistence.load_notes()
    for (id, value) in notes:
        number_notes[id] = value


def notes_to_str() -> str:
    sorted_notes = sorted(number_notes.items(), key=lambda x: x[0])
    lk = max(map(len, number_notes.keys())) + 1
    lv = max(map(lambda x: len(str(x)), number_notes.values()))
    return "\n".join([f"{k:<{lk}}: {v:>{lv}}" for k, v in sorted_notes])


def create_note(note_id: str, value: int, user: discord.Member) -> str:
    if note_id not in number_notes:
        number_notes[note_id] = 0

    number_notes[note_id] += int(value)
    response = "{user} {note_id} ist jetzt {value}.".format(
        user=user.mention, note_id=note_id, value=number_notes[note_id],
    )
    persistence.persist_note(note_id, number_notes[note_id])
    return response


def get_notes(user: discord.Member) -> str:
    if len(number_notes.items()):
        return "{user}\n```{notes}```".format(user=user.mention, notes=notes_to_str())
    else:
        return "{} Es gibt keine Notizen.".format(user.mention)


def delete_note(user: discord.Member, id: str) -> str:
    if id in number_notes:
        persistence.remove_note(id)
        response = "{user} {id} war {value} und wurde nun gelöscht.".format(
            user=user.mention, id=id, value=number_notes[id]
        )
        del number_notes[id]
        return response
    else:
        return "{user} Es gibt keine Notiz {id}.".format(user=user.mention, id=id)


def create_response(message: str, user: discord.Member) -> str:
    create_match = re.search(
        r"^note:(?P<id>\w+)(->(?P<number>[\+\-]?[0-9]+))?$", message, re.IGNORECASE,
    )
    if create_match:
        return create_note(create_match.group("id"), create_match.group("number"), user)

    get_match = re.search(r"^notes$", message, re.IGNORECASE)
    if get_match:
        return get_notes(user)

    remove_match = re.search(r"^delete note (?P<id>\w+)$", message, re.IGNORECASE)
    if remove_match:
        return delete_note(user, remove_match.group("id"))
