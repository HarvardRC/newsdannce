import sqlite3
import click

from flask import current_app, g

JOB_TABLE = "job"


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # enable foreign keys for sqlite (disabled by default)
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql", mode="r") as f:
        db.executescript(f.read())


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database")
