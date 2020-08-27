import os
from pony import orm

db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


class Spells(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    check = orm.Required(str)
    effect = orm.Required(str)
    casting_time = orm.Required(str)
    ae_cost = orm.Required(str)
    range = orm.Required(str)
    duration = orm.Required(str)
    target_category = orm.Required(str)
    property = orm.Required(str)
    tradition = orm.Required(str)
    improvement_cost = orm.Required(str)
    spell_improvements = orm.Optional(orm.StrArray)
    publication = orm.Required(str)


@orm.db_session
def add(spell):
    sections = {"spell_improvements": []}
    print(spell.title)
    if Spells.exists(url=spell.url):
        return
    for section in spell.body.split("\n\n"):
        kv = section.split(":")
        if len(kv) == 1:
            if "Seite" in kv[0]:
                sections["Publikation"] = kv[0].strip()
        else:
            key, *value = kv
            value = ":".join(value)
            if key.startswith("#"):
                sections["spell_improvements"].append(f"{key}: {value.strip()}")
            else:
                if key.startswith("Publikation"):
                    key = "Publikation"
                sections[key] = value.strip()

    return Spells(
        url=spell.url,
        title=spell.title,
        check=sections["Probe"],
        effect=sections["Wirkung"],
        casting_time=sections["Zauberdauer"],
        ae_cost=sections["AsP-Kosten"],
        range=sections["Reichweite"],
        duration=sections["Wirkungsdauer"],
        target_category=sections["Zielkategorie"],
        property=sections["Merkmal"],
        tradition=sections["Verbreitung"],
        improvement_cost=sections["Steigerungsfaktor"],
        spell_improvements=sections["spell_improvements"],
        publication=sections["Publikation"],
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
