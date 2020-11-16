import re
from datetime import datetime, timedelta
from typing import List, Union, Optional

from pony import orm
from discord import Message, Member

from bot.persistence import db
from bot.response import Response


class Note(db.Entity):
    key = orm.Required(str)
    value = orm.Required(int, size=64)
    server = orm.Required(str)
    changed_at = orm.Required(datetime)
    changed_by = orm.Required(str)
    orm.PrimaryKey(key, server)


@orm.db_session
def get_note(note_id: str, server: str) -> Note:
    return Note.get(key=note_id, server=str(server))


@orm.db_session
def get_all() -> List[Note]:
    return Note.get()[:]


def date_to_str(utc: datetime) -> str:
    delta = datetime.utcnow() - utc
    if delta < timedelta(minutes=2):
        return "a few moments ago"
    if delta < timedelta(hours=1):
        return f"{delta.seconds // 60} minutes ago"
    if delta < timedelta(days=2):
        return f"{delta.seconds // 3600} hours ago"
    if delta < timedelta(days=14):
        return f"{delta.days} days ago"
    if delta < timedelta(days=70):
        return f"{delta.days // 7} weeks ago"
    return "a long time ago"


@orm.db_session
def notes_to_str(server: str) -> str:
    sorted_notes = Note.select(lambda n: n.server == str(server)).order_by(
        Note.changed_at, Note.key
    )
    if len(sorted_notes) == 0:
        raise RuntimeError
    lk = max(map(len, [n.key for n in sorted_notes])) + 1
    lv = max(map(lambda x: len(str(x)), [n.value for n in sorted_notes]))
    return "\n".join(
        [
            f"{n.key:<{lk}} {n.value:>{lv}}      -- {date_to_str(n.changed_at)}"
            for n in sorted_notes
        ]
    )


@orm.db_session
def create_note(
    note_id: str, override: bool, value: Union[int, str], user: Member
) -> str:
    note = Note.get(key=note_id, server=str(user.guild.id))
    if note:
        if override:
            note.value = int(value)
        else:
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
        return f"\n```{notes_to_str(str(user.guild.id))}```"
    except RuntimeError:
        return " Es gibt keine Notizen."


@orm.db_session
def delete_note(user: Member, note_id: str) -> str:
    note = Note.get(key=note_id, server=str(user.guild.id))
    if note:
        note.delete()
        return f" {note.key} war {note.value} und wurde nun gelöscht."
    else:
        return f" Es gibt keine Notiz {note_id}."


def create_response(m: Message) -> Optional[Response]:
    send = m.channel.send
    mention = m.author.mention
    c_match = re.search(
        r"^(note|notiz):? ?(?P<id>[\w#]+) ?((?P<op>(->|=)) ?(?P<number>[\+\-]?[0-9]+))?$",
        m.content,
        re.I,
    )
    if c_match:
        note = create_note(
            c_match.group("id"),
            c_match.group("op") == "=",
            c_match.group("number"),
            m.author,
        )
        return Response(send, f"{mention} {note.key} ist jetzt {note.value}.")

    get_match = re.search(r"^(notes|notizen)$", m.content, re.I)
    if get_match:
        return Response(send, mention + get_notes(m.author))

    remove_match = re.search(r"^delete (note|notiz) (?P<id>[\w#]+)$", m.content, re.I)
    if remove_match:
        return Response(send, mention + delete_note(m.author, remove_match.group("id")))

    return None
