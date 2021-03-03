import re
from datetime import datetime

from typing import Optional

from pony import orm
from discord import Member, Message

from bot.persistence import db
from bot.response import Response


class Statistic(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    user = orm.Required(str)
    roll_type = orm.Required(str)
    rolls = orm.Required(orm.IntArray)
    sides = orm.Required(int)
    server = orm.Required(str)
    created_at = orm.Required(datetime)


@orm.db_session
def save_check(
    user: Member,
    roll_type: str,
    rolls: [int],
    sides: int,
):
    rowcount = Statistic.select().count()
    limit = 2000
    delete_rows = rowcount - limit

    if delete_rows > 0:
        min_id = orm.min(s.id for s in Statistic)
        orm.delete(stat for stat in Statistic if stat.id <= min_id + delete_rows + 100)

    return Statistic(
        user=str(user),
        roll_type=roll_type,
        rolls=rolls,
        sides=sides,
        server=str(user.guild.id),
        created_at=datetime.utcnow(),
    )


@orm.db_session
def statistics_to_str(server: str) -> str:
    sides = orm.select(s.sides for s in Statistic)

    if len(sides) == 0:
        raise RuntimeError

    results = []

    for side in sides:
        checks = Statistic.select(lambda n: n.server == str(server) and n.sides == side)
        rolls = [roll for c in checks for roll in c.rolls]
        result_string = f"W{side}:\n"

        for i in range(side):
            count = len([roll for roll in rolls if roll == i + 1])
            result_string += f"{i+1:2} -> {count}\n"
        results.append(result_string)
    return "\n\n".join(results)


def get_statistics(user: Member) -> str:
    try:
        return f"\n```{statistics_to_str(str(user.guild.id))}```"
    except RuntimeError:
        return " Keine Würfelergebnisse gespeichert."


def create_response(m: Message) -> Optional[Response]:
    send = m.channel.send
    mention = m.author.mention

    get_match = re.search(r"^(stats)$", m.content, re.I)
    if get_match:
        return Response(send, mention + get_statistics(m.author))

    return None
