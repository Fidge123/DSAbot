import os
from pony import orm

db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


class Cantrips(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    effect = orm.Required(str)
    range = orm.Required(str)
    duration = orm.Required(str)
    target_category = orm.Required(str)
    property = orm.Required(str)
    comment = orm.Optional(str)
    publication = orm.Required(str)


@orm.db_session
def add(cantrip):
    sections = {}
    if Cantrips.exists(url=cantrip.url):
        return
    for section in cantrip.body.split("\n\n"):
        kv = section.split(":")
        if len(kv) == 1:
            if "Seite" in kv[0]:
                sections["Publikation"] = kv[0].strip()
            if kv[0].strip() != "":
                sections["effect"] = kv[0].strip()
        else:
            key, value = kv
            if key == "Publikation(en)":
                key = "Publikation"
            sections[key] = value.strip()

    return Cantrips(
        url=cantrip.url,
        title=cantrip.title,
        effect=sections["effect"],
        range=sections["Reichweite"],
        duration=sections["Wirkungsdauer"],
        target_category=sections["Zielkategorie"],
        property=sections["Merkmal"],
        comment=sections.get("Anmerkung", ""),
        publication=sections["Publikation"],
    )


@orm.db_session
def get():
    return Regelwiki.select(
        lambda r: r.parents[0] == "Magie" and r.parents[1] == "Zaubertricks"
    )[:]


DB_URL = os.getenv("HEROKU_POSTGRESQL_COBALT_URL") or os.getenv("DATABASE_URL")
if DB_URL:
    db.bind(provider="postgres", dsn=DB_URL)
    db.generate_mapping(create_tables=True)
else:
    raise NotImplementedError(
        "DATABASE_URL needs to be defined to connect to a PostgreSQL"
    )

for cantrip in get():
    add(cantrip)
