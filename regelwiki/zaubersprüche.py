import os
from pony import orm

db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


class Zaubersprüche(db.Entity):
    url = orm.PrimaryKey(str)
    Titel = orm.Required(str)
    Probe = orm.Required(str)
    Wirkung = orm.Required(str)
    Zauberdauer = orm.Required(str)
    AsP_Kosten = orm.Required(str)
    Reichweite = orm.Required(str)
    Wirkungsdauer = orm.Required(str)
    Zielkategorie = orm.Required(str)
    Merkmal = orm.Required(str)
    Verbreitung = orm.Required(str)
    Steigerungsfaktor = orm.Required(str)
    Zaubererweiterungen = orm.Optional(orm.StrArray)
    Publikation = orm.Required(str)


@orm.db_session
def add(spell):
    sections = {"Zaubererweiterungen": []}
    print(spell.title)
    if Zaubersprüche.exists(url=spell.url):
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
                    sections["Zaubererweiterungen"].append(f"{key}: {value}")
                else:
                    if key.startswith("Publikation"):
                        key = "Publikation"
                    sections[key] = value

    return Zaubersprüche(
        url=spell.url,
        Titel=spell.title,
        Probe=sections["Probe"],
        Wirkung=sections["Wirkung"],
        Zauberdauer=sections["Zauberdauer"],
        AsP_Kosten=sections["AsP_Kosten"],
        Reichweite=sections["Reichweite"],
        Wirkungsdauer=sections["Wirkungsdauer"],
        Zielkategorie=sections["Zielkategorie"],
        Merkmal=sections["Merkmal"],
        Verbreitung=sections["Verbreitung"],
        Steigerungsfaktor=sections["Steigerungsfaktor"],
        Zaubererweiterungen=sections["Zaubererweiterungen"],
        Publikation=sections["Publikation"],
    )


@orm.db_session
def get():
    return Regelwiki.select(
        lambda r: r.parents[0] == "Magie" and r.parents[1] == "Zaubersprüche"
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
