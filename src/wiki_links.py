import os

import requests
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


@orm.db_session
def parse(url, parents=[]):
    if Regelwiki.exists(url=url):
        return Regelwiki[url]
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "lxml")
    main = soup.find("div", id="main")
    title = soup.title.string.split("- DSA Regel Wiki")[0].strip()
    print(" > ".join(parents), ">", title)

    body = []
    for br in main.find_all("br"):
        br.replace_with("\n")
    for strong in main.find_all("strong"):
        if strong.text.strip():
            strong.replace_with(f"**{strong.text.strip()}**")
    for em in main.find_all("em"):
        if em.text.strip():
            em.replace_with(f"_{em.text.strip()}_")

    table = soup.find("table")
    if table:
        headers = [header.text for header in table.find_all("th")]
        results = [
            f"{headers[i]}: {cell.text.strip()}"
            for i, cell in enumerate(table.find("tbody").find("tr").find_all("td"))
            if len(headers) > i and headers[i].encode("ascii", "ignore")
        ]
        body.append("\n".join(results))
    for p in main.find_all("p"):
        body.append(p.text.strip())
    clean(soup)

    children = [
        base + link["href"]
        for link in soup.find_all("a")
        if validate(link) and link not in categories
    ]

    return Regelwiki(
        title=title,
        url=url,
        body="\n\n".join(body),
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
