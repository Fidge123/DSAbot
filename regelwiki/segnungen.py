import os
from pony import orm

db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


class Segnungen(db.Entity):
    url = orm.PrimaryKey(str)
    Titel = orm.Required(str)
    Wirkung = orm.Required(str)
    Reichweite = orm.Required(str)
    Wirkungsdauer = orm.Required(str)
    Zielkategorie = orm.Required(str)
    Aspekt = orm.Required(str)
    Publikation = orm.Required(str)


@orm.db_session
def add(segnung):
    sections = {}
    print(segnung.title)
    if Segnungen.exists(url=segnung.url):
        return
    for section in segnung.body.split("\n\n"):
        kv = section.split(":")
        if len(kv) == 1:
            if "Seite" in kv[0] and len(kv[0]) < 150:
                sections["Publikation"] = kv[0].strip()
            elif kv[0].strip() != "":
                sections["Wirkung"] = kv[0].strip()
        else:
            key, *value = kv
            key = key.replace("-", "_")
            value = ":".join(value).strip()
            if value:
                if key.startswith("Publikation"):
                    key = "Publikation"
                sections[key] = value

    return Segnungen(
        url=segnung.url,
        Titel=segnung.title,
        Wirkung=sections["Wirkung"],
        Reichweite=sections["Reichweite"],
        Wirkungsdauer=sections["Wirkungsdauer"],
        Zielkategorie=sections["Zielkategorie"],
        Aspekt=sections["Aspekt"],
        Publikation=sections["Publikation"],
    )


@orm.db_session
def get():
    return Regelwiki.select(
        lambda r: r.parents[0] == "Götterwirken" and r.parents[1] == "Segnungen"
    )[:]


DB_URL = os.getenv("HEROKU_POSTGRESQL_COBALT_URL") or os.getenv("DATABASE_URL")
if DB_URL:
    db.bind(provider="postgres", dsn=DB_URL)
    db.generate_mapping(create_tables=True)
else:
    raise NotImplementedError(
        "DATABASE_URL needs to be defined to connect to a PostgreSQL"
    )

for segnung in get():
    add(segnung)
