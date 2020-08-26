import re
import os
from typing import Optional, List, Any

from discord import Member, Message
import psycopg2

DB_URL = os.getenv("HEROKU_POSTGRESQL_COBALT_URL")


def next(user: Member, hits: List[Any]):
    yield user.mention
    yield from [
        "{} ({}): <{}>".format(hit["title"], hit["score"], hit["url"]) for hit in hits
    ]


def find(search_string: str) -> List[Any]:
    with psycopg2.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT title, url, body, word_similarity(%s, title) FROM regelwiki ORDER BY 4 DESC LIMIT 5",
                (search_string,),
            )
            return [
                {
                    "title": result[0],
                    "url": result[1],
                    "body": result[2],
                    "score": result[3],
                }
                for result in cur.fetchall()
            ]


def create_response(message: Message) -> Optional[str]:
    match = re.search(r"^wiki\ (?P<search>.*)$", message.content, re.IGNORECASE)
    if match:
        hits = find(match.group("search"))
        return "\n".join(next(message.author, hits))

        # if hits[0]["score"] == 1 and hits[0]["body"]:
        #     body = hits[0]["body"]
        #     for section in body.split("\n\n"):
        #         if len(section) < 1024:
        #             return message.author.send(section), None
        #         else:
        #             return message.author.send(section[:1020] + "..."), None
