import os
from pony import orm

db = orm.Database()


class Regelwiki(db.Entity):
    url = orm.PrimaryKey(str)
    title = orm.Required(str)
    body = orm.Optional(str)
    children = orm.Optional(orm.StrArray)
    parents = orm.Optional(orm.StrArray)


class Magische_Handlungen(db.Entity):
    url = orm.PrimaryKey(str)
    Titel = orm.Required(str)
    Art = orm.Required(str)
    Probe = orm.Required(str)
    Wirkung = orm.Required(str)
    AsP_Kosten = orm.Required(str)
    Talent = orm.Optional(str)
    Zauberdauer = orm.Optional(str)
    Dauer = orm.Optional(str)
    Reichweite = orm.Optional(str)
    Wirkungsdauer = orm.Optional(str)
    Zielkategorie = orm.Optional(str)
    Merkmal = orm.Required(str)
    Voraussetzungen = orm.Optional(str)
    Stammestradition = orm.Optional(str)
    Musiktradition = orm.Optional(str)
    Steigerungsfaktor = orm.Optional(str)
    Publikation = orm.Optional(str)


@orm.db_session
def add(magic_act):
    art = magic_act.parents[2]
    sections = {"Art": art}
    print(magic_act.title)
    if Magische_Handlungen.exists(url=magic_act.url):
        return

    if art == "Hexenflüche":
        sections["Zauberdauer"] = "min. 1 Aktion"
        sections["Steigerungsfaktor"] = "B"
        sections["Reichweite"] = "64 Schritt"
    if art == "Zaubermelodien":
        sections["Zauberdauer"] = "min. 1 Aktion"
        sections["Reichweite"] = "20 Schritt"
        sections["Wirkungsdauer"] = "5 Minuten"
        sections["Publikation"] = "Aventurische Magie I Seite 44 ff."
    if art == "Zaubertänze":
        sections["Zauberdauer"] = "min. 1 Aktion"
        sections["Reichweite"] = "20 Schritt"
        sections["Wirkungsdauer"] = "5 Minuten"
        sections["Publikation"] = "Aventurische Magie I Seite 58 ff."
    if art == "Animistenkräfte":
        sections["Zauberdauer"] = "1 Aktion"
        sections["Reichweite"] = "selbst"
        sections["Zielkategorie"] = "selbst"
    if art == "Herrschaftsrituale":
        sections["Zauberdauer"] = "8 Stunden"
        sections["Reichweite"] = "ganzer Kontinent"
        sections["Steigerungsfaktor"] = "B"
    if art == "Geodenrituale":
        sections["Steigerungsfaktor"] = "B"

    for section in magic_act.body.split("\n\n"):
        kv = section.split(":")
        if len(kv) == 1:
            if "Seite" in kv[0]:
                sections["Publikation"] = kv[0].strip()
        else:
            key, *value = kv
            key = key.replace("-", "_")
            value = ":".join(value).strip()
            if value:
                if key.startswith("Publikation"):
                    key = "Publikation"
                sections[key] = value

    return Magische_Handlungen(
        url=magic_act.url,
        Titel=magic_act.title,
        Art=sections["Art"],
        Probe=sections["Probe"],
        Wirkung=sections["Wirkung"],
        AsP_Kosten=sections.get("AsP_Kosten", "ERROR"),
        Talent=sections.get("Talent", ""),
        Zauberdauer=sections.get("Zauberdauer", ""),
        Dauer=sections.get("Dauer", ""),
        Reichweite=sections.get("Reichweite", ""),
        Wirkungsdauer=sections.get("Wirkungsdauer", ""),
        Zielkategorie=sections.get("Zielkategorie", ""),
        Merkmal=sections["Merkmal"],
        Voraussetzungen=sections.get("Voraussetzungen", ""),
        Stammestradition=sections.get("Stammestradition", ""),
        Musiktradition=sections.get("Musiktradition", ""),
        Steigerungsfaktor=sections.get("Steigerungsfaktor", ""),
        Publikation=sections.get("Publikation", ""),
    )


# TODO: Steinmacht, Ängste mehren, Viehverstümmelung, Melodie der Ermutigung
# Gestalt aus Rauch (Geodenrituale), Melodie der Heilung


@orm.db_session
def get():
    return Regelwiki.select(
        lambda r: r.parents[0] == "Magie"
        and r.parents[1] == "Magische Handlungen"
        and len(r.parents) == 3
    )[:]


DB_URL = os.getenv("HEROKU_POSTGRESQL_COBALT_URL") or os.getenv("DATABASE_URL")
if DB_URL:
    db.bind(provider="postgres", dsn=DB_URL)
    db.generate_mapping(create_tables=True)
else:
    raise NotImplementedError(
        "DATABASE_URL needs to be defined to connect to a PostgreSQL"
    )

for ritual in get():
    add(ritual)
