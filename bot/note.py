import re
from datetime import datetime, timezone
from typing import List, Union, Optional, Tuple

from pony import orm
from discord import Message, Member, Embed

from bot.persistence import db


class Note(db.Entity):
    key = orm.Required(str)
    value = orm.Required(int, size=64)
    server = orm.Required(str)
    changed_at = orm.Required(datetime)
    changed_by = orm.Required(str)
    orm.PrimaryKey(key, server)


@orm.db_session
def get_note(note_id, server) -> Note:
    return Note.get(key=note_id, server=str(server))


@orm.db_session
def get_all() -> List[Note]:
    return Note.get()[:]


def date_to_str(utc: datetime) -> str:
    input_as_local = utc.replace(tzinfo=timezone.utc).astimezone()
    if datetime.now().date() == input_as_local.date():
        return input_as_local.strftime("%H:%M")
    if datetime.now().year == input_as_local.year:
        return input_as_local.strftime("%d.%m. %H:%M")
    return input_as_local.strftime("%d.%m.%y")


@orm.db_session
def notes_to_str(guild) -> str:
    sorted_notes = Note.select(lambda n: n.server == str(guild)).order_by(Note.key)
    if len(sorted_notes) == 0:
        raise RuntimeError
    lk = max(map(len, [n.key for n in sorted_notes])) + 1
    lv = max(map(lambda x: len(str(x)), [n.value for n in sorted_notes]))
    return "\n".join(
        [
            f"{n.key:<{lk}}: {n.value:>{lv}} ({date_to_str(n.changed_at)})"
            for n in sorted_notes
        ]
    )


@orm.db_session
def create_note(note_id: str, value: Union[int, str], user: Member) -> str:
    note = Note.get(key=note_id, server=str(user.guild.id))
    if note:
        note.value += int(value)
        note.changed_at = datetime.utcnow()
        note.changed_by = str(user)
    else:
        note = Note(
            key=note_id,
            value=value,
            server=str(user.guild.id),
            changed_at=datetime.utcnow(),
            changed_by=str(user),
        )

    return note


def get_notes(user: Member) -> str:
    try:
        return "{user}\n```{notes}```".format(
            user=user.mention, notes=notes_to_str(user.guild.id)
        )
    except RuntimeError:
        return "{} Es gibt keine Notizen.".format(user.mention)


@orm.db_session
def delete_note(user: Member, note_id: str) -> str:
    note = Note.get(key=note_id, server=str(user.guild.id))
    if note:
        note.delete()
        return "{user} {id} war {value} und wurde nun gelöscht.".format(
            user=user.mention, id=note.key, value=note.value
        )
    else:
        return "{user} Es gibt keine Notiz {id}.".format(user=user.mention, id=note_id)


def create_response(message: Message) -> Optional[Tuple[str, Embed]]:
    content = message.content
    create_match = re.search(
        r"^note:(?P<id>[\w#]+)(->(?P<number>[\+\-]?[0-9]+))?$", content, re.IGNORECASE,
    )
    if create_match:
        note = create_note(
            create_match.group("id"), create_match.group("number"), message.author
        )
        return (
            "{user} {note_id} ist jetzt {value}.".format(
                user=message.author.mention, note_id=note.key, value=note.value,
            ),
            None,
        )

    get_match = re.search(r"^notes$", content, re.IGNORECASE)
    if get_match:
        return get_notes(message.author), None

    remove_match = re.search(r"^delete note (?P<id>[\w#]+)$", content, re.IGNORECASE)
    if remove_match:
        return delete_note(message.author, remove_match.group("id")), None
    return None
