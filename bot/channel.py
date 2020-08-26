from datetime import datetime
from typing import Optional

from pony import orm
from discord import Message

from bot.response import Response
from bot.persistence import db


class Channel(db.Entity):
    id = orm.PrimaryKey(str)
    server = orm.Required(str)
    added_at = orm.Required(datetime)
    added_by = orm.Required(str)


@orm.db_session
def is_permitted(channel_id) -> bool:
    return Channel.exists(id=str(channel_id))


@orm.db_session
async def add_channel(message: Message):
    if not is_permitted(message.channel.id) and "SUMMON" == message.content:
        Channel(
            id=str(message.channel.id),
            server=str(message.channel.guild.id),
            added_at=datetime.utcnow(),
            added_by=str(message.author),
        )
        await message.channel.send("I'm listening for rolls here!")


@orm.db_session
def create_response(message: Message) -> Optional[Response]:
    if "SUMMON" == message.content:
        return Response(message.channel.send, "I am already listening")

    if "BEGONE" == message.content:
        Channel.get(id=str(message.channel.id)).delete()
        return Response(message.channel.send, "I have left")

    return None
