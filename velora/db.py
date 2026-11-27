import sqlite3
from pathlib import Path

import click
from flask import current_app, g

PRODUCTS = [
    ("VL-101", "Field Notebook", "A pocket notebook with dot-grid pages and a stitched blue cover.", 850),
    ("VL-102", "Studio Tray", "A shallow clay tray for pencils and small desk tools.", 2400),
    ("VL-103", "Pocket Ruler", "A brushed steel ruler marked in centimetres.", 675),
]


def connection():
    if "database" not in g:
        g.database = sqlite3.connect(current_app.config["DATABASE"])
        g.database.row_factory = sqlite3.Row
    return g.database


def close_connection(error):
    database = g.pop("database", None)
    if database is not None:
        database.close()


def init_app(app):
    app.teardown_appcontext(close_connection)

    @app.cli.command("init-db")
    def init_db():
        Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
        with app.open_resource("schema.sql", mode="r") as schema:
            connection().executescript(schema.read())
        click.echo("Catalog schema ready.")

    @app.cli.command("seed-demo")
    def seed_demo():
        with connection() as database:
            database.executemany(
                "INSERT INTO products (sku, name, description, price_cents) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(sku) DO NOTHING", PRODUCTS
            )
        click.echo("Demo catalog ready.")
