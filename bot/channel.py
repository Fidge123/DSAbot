from datetime import datetime
from typing import Tuple, Optional

from pony import orm
from discord import Message, Embed

from bot.persistence import db


class Channel(db.Entity):
    id = orm.PrimaryKey(int)
    server = orm.Required(int)
    added_at = orm.Required(datetime)
    added_by = orm.Required(str)


@orm.db_session
def is_permitted(content: str, message: Message) -> bool:
    permitted = Channel.exists(id=message.channel.id)
    if not permitted and "SUMMON" in content:
        Channel(
            id=message.channel.id,
            server=message.channel.guild,
            added_at=datetime.utcnow(),
            added_by=str(message.author),
        )
    return permitted


@orm.db_session
def create_response(content: str, message: Message) -> Optional[Tuple[str, Embed]]:
    if "SUMMON" in content:
        return "I am already listening", None

    if "BEGONE" in content:
        Channel[message.channel.id].delete()
        return "I have left", None
