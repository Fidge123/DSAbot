import os
from pony import orm

db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


class Liturgien(db.Entity):
    url = orm.PrimaryKey(str)
    Titel = orm.Required(str)
    Probe = orm.Required(str)
    Wirkung = orm.Required(str)
    Liturgiedauer = orm.Required(str)
    KaP_Kosten = orm.Required(str)
    Reichweite = orm.Required(str)
    Wirkungsdauer = orm.Required(str)
    Zielkategorie = orm.Required(str)
    Verbreitung = orm.Optional(str)
    Steigerungsfaktor = orm.Optional(str)
    Liturgieerweiterungen = orm.Optional(orm.StrArray)
    Publikation = orm.Required(str)


@orm.db_session
def add(spell):
    sections = {"Liturgieerweiterungen": []}
    print(spell.title)
    if Liturgien.exists(url=spell.url):
        return
    for section in spell.body.split("\n\n"):
        kv = section.split(":")
        if len(kv) == 1:
            if "Seite" in kv[0]:
                sections["Publikation"] = kv[0].strip()
        else:
            key, *value = kv
            key = key.replace("-", "_")
            value = ":".join(value).strip()
            if value:
                if key.startswith("#"):
                    sections["Liturgieerweiterungen"].append(f"{key}: {value}")
                else:
                    if key.startswith("Publikation"):
                        key = "Publikation"
                    sections[key] = value

    return Liturgien(
        url=spell.url,
        Titel=spell.title,
        Probe=sections["Probe"],
        Wirkung=sections["Wirkung"],
        Liturgiedauer=sections["Liturgiedauer"],
        KaP_Kosten=sections["KaP_Kosten"],
        Reichweite=sections["Reichweite"],
        Wirkungsdauer=sections["Wirkungsdauer"],
        Zielkategorie=sections["Zielkategorie"],
        Verbreitung=sections.get("Verbreitung", ""),
        Steigerungsfaktor=sections.get("Steigerungsfaktor", ""),
        Liturgieerweiterungen=sections["Liturgieerweiterungen"],
        Publikation=sections["Publikation"],
    )


@orm.db_session
def get():
    return Regelwiki.select(
        lambda r: r.parents[0] == "Götterwirken" and r.parents[1] == "Liturgien"
    )[:]


DB_URL = os.getenv("HEROKU_POSTGRESQL_COBALT_URL") or os.getenv("DATABASE_URL")
if DB_URL:
    db.bind(provider="postgres", dsn=DB_URL)
    db.generate_mapping(create_tables=True)
else:
    raise NotImplementedError(
        "DATABASE_URL needs to be defined to connect to a PostgreSQL"
    )

for spell in get():
    add(spell)
