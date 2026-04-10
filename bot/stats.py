import json
import re
from datetime import datetime

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
    rolls: list[int],
    sides: int,
):
    rowcount = Statistic.select().count()
    limit = 2000
    delete_rows = rowcount - limit

    if delete_rows > 0:
        oldest = Statistic.select().order_by(Statistic.id)[:1][0]
        threshold = int(oldest.id + delete_rows + 100)
        db.execute(f"DELETE FROM statistic WHERE id <= {threshold}")

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
    # pony ORM is incompatible with Python 3.14 in two ways:
    #   1. select(lambda ...) uses a bytecode decompiler that fails on 3.14's changed
    #      generator frame format.
    #   2. select(prop=value) fails with a deepcopy error on itertools.count inside
    #      _apply_kwargs().
    # Raw SQL via db.execute() bypasses both issues until pony adds Python 3.14 support.
    # SQLite stores IntArray as a JSON string; PostgreSQL returns a native list.
    rows = list(
        db.execute(
            "SELECT rolls, sides FROM statistic WHERE server = $server",
            globals={"server": server},
        )
    )
    if not rows:
        raise RuntimeError

    sides_rolls: dict[int, list[int]] = {}
    for rolls_raw, side in rows:
        rolls = json.loads(rolls_raw) if isinstance(rolls_raw, str) else list(rolls_raw)
        sides_rolls.setdefault(side, []).extend(rolls)

    results = []
    for side, rolls in sorted(sides_rolls.items()):
        result_string = f"W{side}:\n"
        for i in range(side):
            result_string += f"{i + 1:2} -> {rolls.count(i + 1)}\n"
        results.append(result_string)
    return "\n\n".join(results)


def get_statistics(user: Member) -> str:
    try:
        return f"\n```{statistics_to_str(str(user.guild.id))}```"
    except RuntimeError:
        return " Keine Würfelergebnisse gespeichert."


def create_response(m: Message) -> Response | None:
    send = m.channel.send
    mention = m.author.mention

    get_match = re.search(r"^(stats)$", m.content, re.I)
    if get_match:
        return Response(send, mention + get_statistics(m.author))

    return None
