import os
from pony import orm

db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


class Zeremonien(db.Entity):
    url = orm.PrimaryKey(str)
    Titel = orm.Required(str)
    Probe = orm.Required(str)
    Wirkung = orm.Required(str)
    Zeremoniedauer = orm.Required(str)
    KaP_Kosten = orm.Required(str)
    Reichweite = orm.Required(str)
    Wirkungsdauer = orm.Required(str)
    Zielkategorie = orm.Required(str)
    Verbreitung = orm.Required(str)
    Steigerungsfaktor = orm.Optional(str)
    Liturgieerweiterungen = orm.Optional(orm.StrArray)
    Publikation = orm.Optional(str)


@orm.db_session
def add(ceremony):
    sections = {"Liturgieerweiterungen": []}
    print(ceremony.title)
    if Zeremonien.exists(url=ceremony.url):
        return
    for section in ceremony.body.split("\n\n"):
        kv = section.split(":")
        if len(kv) == 1:
            if "Seite" in kv[0]:
                sections["Publikation"] = kv[0].strip()
        else:
            key, *value = kv
            key = key.replace("-", "_")
            value = ":".join(value).strip()
            if value:
                if key == "Merkmal":
                    sections["Verbreitung"] = value
                if key.startswith("#"):
                    sections["Liturgieerweiterungen"].append(f"{key}: {value}")
                else:
                    if key.startswith("Publikation"):
                        key = "Publikation"
                    sections[key] = value

    return Zeremonien(
        url=ceremony.url,
        Titel=ceremony.title,
        Probe=sections["Probe"],
        Wirkung=sections["Wirkung"],
        Zeremoniedauer=sections["Zeremoniedauer"],
        KaP_Kosten=sections["KaP_Kosten"],
        Reichweite=sections["Reichweite"],
        Wirkungsdauer=sections["Wirkungsdauer"],
        Zielkategorie=sections["Zielkategorie"],
        Verbreitung=sections["Verbreitung"],
        Steigerungsfaktor=sections.get("Steigerungsfaktor", ""),
        Liturgieerweiterungen=sections["Liturgieerweiterungen"],
        Publikation=sections.get("Publikation", ""),
    )


# TODO Ackersegen


@orm.db_session
def get():
    return Regelwiki.select(
        lambda r: r.parents[0] == "Götterwirken" and r.parents[1] == "Zeremonien"
    )[:]


DB_URL = os.getenv("HEROKU_POSTGRESQL_COBALT_URL") or os.getenv("DATABASE_URL")
if DB_URL:
    db.bind(provider="postgres", dsn=DB_URL)
    db.generate_mapping(create_tables=True)
else:
    raise NotImplementedError(
        "DATABASE_URL needs to be defined to connect to a PostgreSQL"
    )

for ceremony in get():
    add(ceremony)
