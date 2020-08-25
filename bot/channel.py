from datetime import datetime
from typing import Tuple, Optional

from pony import orm
from discord import Message, Embed

from bot.persistence import db


class Channel(db.Entity):
    id = orm.PrimaryKey(str)
    server = orm.Required(str)
    added_at = orm.Required(datetime)
    added_by = orm.Required(str)


@orm.db_session
def is_permitted(content: str, message: Message) -> bool:
    permitted = Channel.exists(id=str(message.channel.id))
    if not permitted and "SUMMON" in content:
        Channel(
            id=str(message.channel.id),
            server=str(message.channel.guild.id),
            added_at=datetime.utcnow(),
            added_by=str(message.author),
        )
        message.channel.send("I'm listening for rolls here!")
    return permitted


@orm.db_session
def create_response(content: str, message: Message) -> Optional[Tuple[str, Embed]]:
    if "SUMMON" in content:
        return "I am already listening", None

    if "BEGONE" in content:
        Channel.get(id=str(message.channel.id)).delete()
        return "I have left", None

    return None
