import json
import re
from typing import Optional, List, Tuple, Any

from discord import Member, Embed
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
import requests


def score(a: str, b: str) -> float:
    return fuzz.partial_ratio(a, b) / 2 + fuzz.token_set_ratio(a, b) / 2


def search(search_string: str, site_map: List[Any]):
    for site in site_map:
        yield from search(search_string, site["subpages"])
        yield {
            "title": site["title"],
            "url": site["url"],
            "score": score(site["title"].lower(), search_string.lower()),
        }


def next(user: Member, hits: List[Any]):
    yield user.mention
    yield from [
        "{} ({}): <{}>".format(hit["title"], hit["score"], hit["url"]) for hit in hits
    ]


regelwiki = []

with open("regelwiki.json") as rw_json:
    regelwiki = json.loads(rw_json.read())


def find(search_string: str) -> List[Any]:
    hits = sorted(
        search(search_string, regelwiki), key=lambda x: x["score"], reverse=True
    )

    return [hit for hit in hits if hit["score"] >= 75][:5] or hits[:3]


def create_response(message: str, user: Member) -> Optional[Tuple[str, Embed]]:
    match = re.search(r"^wiki\ (?P<search>.*)$", message, re.IGNORECASE)
    if match:
        hits = find(match.group("search"))
        embed = None
        if hits[0]["score"] == 100:
            try:
                res = requests.get(hits[0]["url"])
                soup = BeautifulSoup(res.text, "lxml")
                for br in soup.find_all("br"):
                    br.replace_with("\n")
                para = soup.find("div", id="main").find_all("p")
                fields = [p.text.split(":") for p in para]
                embed = Embed(**hits[0], description="Auszug vom Ulisses Regelwiki")
                for field in fields:
                    if len(field) == 2 and field[0] and field[1] and len(embed) < 5000:
                        embed.add_field(name=field[0][:128], value=field[1][:512])
            except:
                pass

        return "\n".join(next(user, hits)), embed
    return None
