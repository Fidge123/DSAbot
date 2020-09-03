import os

import requests
import htmlmin
from bs4 import BeautifulSoup
from pony import orm

base = "http://ulisses-regelwiki.de/"
blacklist = [
    "index.php/start.html",
    "index.php/kontakt.html",
    "index.php/impressum.html",
    "index.php/datenschutzerklaerung.html",
]
db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    html = orm.Required(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


def validate(link):
    try:
        return (
            link["href"].startswith("index.php")
            and "#" not in link["href"]
            and link["href"] not in blacklist
        )
    except:
        return False


def clean(soup):
    soup.header.decompose()
    soup.footer.decompose()
    for form in soup.find_all("form"):
        form.decompose()

    for bc in soup.find_all("div", class_="breadcrumb_boxed"):
        bc.decompose()

    soup.find("div", id="main").decompose()


def get_content(soup) -> str:
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for strong in soup.find_all("strong"):
        if strong.text.strip():
            strong.replace_with(f"**{strong.text.strip()}**")
    for em in soup.find_all("em"):
        if em.text.strip():
            em.replace_with(f"_{em.text.strip()}_")

    content = []

    for el in soup.find_all(["table", "p"]):
        if el.name == "table" and el.thead:
            headers = [header.text for header in el.find_all("th")]
            results = [
                f"{headers[i]}: {cell.text.strip()}"
                for i, cell in enumerate(el.find("tbody").find("tr").find_all("td"))
                if len(headers) > i
            ]
            content.append("\n".join(results))
        if el.name == "table" and not el.thead:
            results = [
                f"{row.contents[0].text.strip()}: {row.contents[0].text.strip()}"
                for row in el.find("tbody").find_all("tr")
                if len(row.contents) == 2
            ]
            content.append("\n".join(results))
        if el.name == "p" and el.text.strip():
            content.append(el.text.strip())
    return "\n\n".join(content)


def get_children(soup):
    clean(soup)
    return [
        base + link["href"]
        for link in soup.find_all("a")
        if validate(link) and link not in categories
    ]


@orm.db_session
def parse(url, parents=[]):
    input_html = ""
    rw = Regelwiki.get(url=url)
    if rw:
        input_html = rw.html
    else:
        res = requests.get(url)
        input_html = res.text
    soup = BeautifulSoup(htmlmin.minify(input_html), "lxml",)
    html = str(soup)
    title = soup.title.string.split("- DSA Regel Wiki")[0].strip()

    print(" > ".join(parents), ">", title)

    body = get_content(soup.find("div", id="main"))
    children = get_children(soup)

    if rw:
        rw.title = title
        rw.html = html
        rw.body = body
        rw.children = children
        rw.parents = parents
        return rw
    else:
        return Regelwiki(
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
    site = parse(url, parents)
    p = site.parents[:]
    p.append(site.title)
    for child in site.children:
        queue.append((child, p))
