import os
from pony import orm

db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


class Talente(db.Entity):
    url = orm.Required(str)
    Titel = orm.PrimaryKey(str)
    Kategorie = orm.Required(str)
    Probe = orm.Required(str)
    Anwendungsgebiete = orm.Required(str)
    Belastung = orm.Required(str)
    Werkzeuge = orm.Optional(str)
    Qualität = orm.Required(str)
    Misslungene_Probe = orm.Required(str)
    Kritischer_Erfolg = orm.Required(str)
    Patzer = orm.Required(str)
    Steigerungskosten = orm.Required(str)


@orm.db_session
def add(talent, category, url):
    titel, *data = talent.split("\n\n")
    titel = titel.strip()
    sections = {"Titel": titel}
    print(titel)
    if titel.startswith("Publikation") or Talente.exists(Titel=titel):
        return

    last_key = ""
    for section in data:
        kv = section.split(":")
        if len(kv) == 1:
            sections[last_key] += kv[0]
        else:
            key, *value = kv
            key = key.replace(" ", "_")
            last_key = key
            value = ":".join(value).strip()
            if value:
                if key.startswith("Publikation"):
                    key = "Publikation"
                sections[key] = value

    return Talente(
        url=url,
        Kategorie=category,
        Titel=sections["Titel"],
        Probe=sections["Probe"],
        Anwendungsgebiete=sections["Anwendungsgebiete"],
        Belastung=sections["Belastung"],
        Werkzeuge=sections.get("Werkzeuge", ""),
        Qualität=sections["Qualität"],
        Misslungene_Probe=sections["Misslungene_Probe"],
        Kritischer_Erfolg=sections["Kritischer_Erfolg"],
        Patzer=sections["Patzer"],
        Steigerungskosten=sections["Steigerungskosten"],
    )


@orm.db_session
def get():
    return Regelwiki.select(lambda r: r.parents[2] == "Talente")[:]


DB_URL = os.getenv("DATABASE_URL")
if DB_URL:
    db.bind(provider="postgres", dsn=DB_URL)
    db.generate_mapping(create_tables=True)
else:
    raise NotImplementedError(
        "DATABASE_URL needs to be defined to connect to a PostgreSQL"
    )

for talente in get():
    for talent in talente.body.split("\n\n\n\n"):
        add(talent, talente.title, talente.url)
