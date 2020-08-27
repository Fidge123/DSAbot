import re
import os
from typing import Optional, List, Any

from discord import Member, Message
import psycopg2

from bot.response import Response

DB_URL = os.getenv("HEROKU_POSTGRESQL_COBALT_URL")


def next(user: Member, hits: List[Any], search_term: str):
    yield user.mention
    yield from [
        "{} ({}%): <{}>".format(hit["title"], hit["score"], hit["url"]) for hit in hits
    ]


def _normalize(score: float, body: str, search_term: str, in_body: bool) -> int:
    if in_body:
        body = body.lower()
        search_term = search_term.lower()
        sections = body.split("\n\n")
        num_contained = len([s for s in sections if search_term in s])
        return int((num_contained / len(sections)) * 100)
    else:
        return int(score * 100)


def find(search_term: str, in_body=False) -> List[Any]:
    title_stmt = "SELECT title, url, body, word_similarity(%s, title) FROM regelwiki ORDER BY 4 DESC LIMIT 5"

    body_stmt = """
        SELECT *
        FROM
            (SELECT
                title,
                url,
                body,
                (length(body) - length(regexp_replace(body, %s, '', 'gi'))) / length(%s) AS o,
                parents
            FROM regelwiki
            ORDER BY 4 DESC
            LIMIT 20) AS i
        WHERE o > 0
        ORDER BY array_length(i.parents, 1), o DESC
        LIMIT 5
        """

    with psycopg2.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            if in_body:
                cur.execute(body_stmt, (search_term, search_term))
            else:
                cur.execute(title_stmt, (search_term,))
            return [
                {
                    "title": result[0],
                    "url": result[1],
                    "body": result[2],
                    "score": _normalize(result[3], result[2], search_term, in_body),
                }
                for result in cur.fetchall()
            ]


def filter_hits(hits: List[Any]) -> List[Any]:
    return [hit for hit in hits if hit["score"] + 20 > hits[0]["score"]]


def create_response(message: Message) -> Optional[Response]:
    match = re.search(r"^wiki\ (?P<search>.*)$", message.content, re.I)
    if match:
        search_term = match.group("search")
        title_match = filter_hits(find(search_term))

        if title_match[0]["score"] < 60:
            body_match = find(search_term, True)
            return Response(
                message.channel.send,
                "\n".join(next(message.author, body_match, search_term)),
            )

        response = Response(
            message.channel.send,
            "\n".join(next(message.author, title_match, search_term)),
        )

        perfect_hits = [t for t in title_match if t["score"] == 100 and t["body"]]
        if len(perfect_hits) == 1:
            body = perfect_hits[0]["body"]
            next_message = "**{}**".format(perfect_hits[0]["title"])
            for section in body.split("\n\n"):
                if len(next_message) + len(section) <= 2000:
                    next_message = "\n\n".join([next_message, section])
                else:
                    response.append(message.author.send, next_message[:2000])
                    next_message = section
            if next_message:
                response.append(message.author.send, next_message)
        return response

    return None
