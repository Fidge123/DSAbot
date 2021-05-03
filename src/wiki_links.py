import os
import re

import requests
import htmlmin
from bs4 import BeautifulSoup
from pony import orm

base = "https://ulisses-regelwiki.de/"
blacklist = [
    "/index.php/tde-games-reference-en.html",
    "index.php/start.html",
    "index.php/kontakt.html",
    "index.php/impressum.html",
    "index.php/datenschutzerklaerung.html",
]
db = orm.Database()


class RegelwikiNeu(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    html = orm.Required(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


def validate(link):
    try:
        return "index.php" not in link["href"] and "#" not in link["href"]
    except:
        return False


def clean(soup, keep_main):
    soup.header.decompose()
    soup.footer.decompose()
    for form in soup.find_all("form"):
        form.decompose()

    for bc in soup.find_all("div", class_="breadcrumb_boxed"):
        bc.decompose()

    if not keep_main:
        soup.find("div", id="main").decompose()


def get_spell_content(body) -> str:
    for br in body.find_all("br"):
        br.replace_with("\n")

    for spalte in body.find_all("div", class_="spalte1"):
        stripped = spalte.text.strip()
        if stripped:
            spalte.replace_with(f"\n\n**{stripped}**")

    for line in body.find_all("div", class_="body_einzeln"):
        stripped = line.text.strip()
        if stripped:
            pre, post = line.text.split(stripped)
            line.replace_with(f"\n\n{pre}**{stripped}**{post}\n\n")

    text = body.text.strip()

    return "\n\n#".join([x.strip() for x in text.split("#")])


def colon(key, value):
    return ": ".join(
        [el for el in [key, value,] if el.encode("ascii", errors="ignore")]
    )


def get_content(soup, url) -> str:
    for strong in soup.find_all(["strong", "b"]):
        stripped = strong.text.strip()
        if stripped:
            pre, post = strong.text.split(stripped)
            strong.replace_with(f"{pre}**{stripped}**{post}")
    for em in soup.find_all(["em", "i"]):
        stripped = em.text.strip()
        if stripped:
            pre, post = em.text.split(stripped)
            em.replace_with(f"{pre}_{stripped}_{post}")

    spell_content = ""
    try:
        body = soup.find("div", class_="grid").find("div", class_="body").extract()
        spell_content = get_spell_content(body)
    except:
        pass

    content = []

    for el in soup.find_all(["table", "p"]):
        if el.name == "table":
            rows = len(el.find_all("tr"))
            columns = len(el.find("tbody").find("tr").find_all(["th", "td"]))
            if rows == 2:
                headers = [header.text.strip() for header in el.find_all("th")]
                results = [
                    colon(headers[i], cell.text.strip())
                    for i, cell in enumerate(el.find("tbody").find("tr").find_all("td"))
                    if len(headers) > i
                ]
                content.append("\n".join(results))
            if columns == 2:
                results = [
                    colon(
                        row.find_all(["th", "td"])[0].text.strip(),
                        row.find_all(["th", "td"])[1].text.strip(),
                    )
                    for row in el.find("tbody").find_all("tr")
                ]
                content.append("\n".join(results))
        if el.name == "p" and el.text.strip():
            for br in el.find_all("br"):
                br.replace_with("\n")
            content.append(el.text.strip())

    if spell_content and content:
        print(url)

    return "\n\n".join([spell_content] + content)


def get_children(soup, keep_main):
    clean(soup, keep_main)
    return [
        base + link["href"]
        for link in soup.find_all("a")
        if validate(link) and link not in categories
    ]


def repair(input_html, url):
    try:
        repaired = re.sub(
            r"<!DOCTYPE html>[\W]*<html>[\w\W]*<body>([\w\W]*?)<\/body>[\W]*<\/html>",
            r"\g<1>",
            input_html,
            re.M,
        )
        return htmlmin.minify(repaired)
    except:
        print(f"Could not repair - {url}")
        return input_html


def minify(input_html, url):
    try:
        return htmlmin.minify(input_html)
    except:
        return repair(input_html, url)


@orm.db_session
def parse(url, parents=[], allow_skipping=True):
    input_html = ""
    rw = RegelwikiNeu.get(url=url)
    if rw and allow_skipping:
        input_html = rw.html
    else:
        res = requests.get(url)
        input_html = res.text
    soup = BeautifulSoup(minify(input_html, url), "lxml",)
    html = str(soup)

    title = ""
    try:
        title = soup.find("div", class_="header").string.strip()
    except:
        title = soup.title.string.split("- DSA Regel Wiki")[0].strip()

    print(" > ".join(parents), ">", title)

    body = get_content(soup.find("div", id="main"), url)
    children = get_children(soup, "auswahl.html" in url)

    if rw:
        rw.title = title
        rw.html = html
        rw.body = body
        rw.children = children
        rw.parents = parents
        return rw
    else:
        return RegelwikiNeu(
            title=title,
            url=url,
            html=html,
            body=body,
            children=children,
            parents=parents,
        )


DB_URL = os.getenv("HEROKU_POSTGRESQL_COBALT_URL") or os.getenv("DATABASE_URL")
if DB_URL:
    db.bind(provider="postgres", dsn=DB_URL)
    db.generate_mapping(create_tables=True)
else:
    raise NotImplementedError(
        "DATABASE_URL needs to be defined to connect to a PostgreSQL"
    )


res = requests.get(base)
soup = BeautifulSoup(res.text, "lxml")
categories = [
    base + link["href"] for link in soup.header.nav.find_all("a") if validate(link)
]
queue = [(category, []) for category in categories]

while len(queue) > 0:
    url, parents = queue.pop(0)
    site = parse(url, parents, True)
    p = site.parents[:]
    p.append(site.title)
    for child in site.children:
        queue.append((child, p))
