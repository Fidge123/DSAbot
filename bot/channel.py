from datetime import datetime
from typing import Optional

from pony import orm
from discord import Message

from bot.persistence import db


class Channel(db.Entity):
    id = orm.PrimaryKey(str)
    server = orm.Required(str)
    added_at = orm.Required(datetime)
    added_by = orm.Required(str)


@orm.db_session
def is_permitted(message: Message) -> bool:
    permitted = Channel.exists(id=str(message.channel.id))
    if not permitted and "SUMMON" == message.content:
        Channel(
            id=str(message.channel.id),
            server=str(message.channel.guild.id),
            added_at=datetime.utcnow(),
            added_by=str(message.author),
        )
        message.channel.send("I'm listening for rolls here!")
    return permitted


@orm.db_session
def create_response(message: Message) -> Optional[str]:
    if "SUMMON" == message.content:
        return "I am already listening"

    if "BEGONE" == message.content:
        Channel.get(id=str(message.channel.id)).delete()
        return "I have left"

    return None
