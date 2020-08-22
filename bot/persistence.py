import os

from pony import orm

db = orm.Database()

if os.getenv("DATABASE_URL"):
    db.bind(provide="postgresql", dsn=os.getenv("DATABASE_URL"))
else:
    db.bind(provider="sqlite", filename="persistence.db", create_db=True)


def on_ready():
    db.generate_mapping(create_tables=True)
    # orm.set_sql_debug(True)
