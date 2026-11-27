import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from .db import connection


@click.command("seed-accounts")
@with_appcontext
def seed_accounts():
    """Create local identities and sample orders after seed-demo."""
    db = connection()
    people = (
        ("avery@example.test", "Avery", "customer"),
        ("morgan@example.test", "Morgan", "customer"),
        ("ops@example.test", "Operations", "admin"),
    )
    orders = (
        ("VC-1001", "avery@example.test", "2026-11-21", "VL-101", 2),
        ("VC-1002", "morgan@example.test", "2026-11-22", "VL-102", 1),
    )
    with db:
        for email, name, role in people:
            if db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
                continue
            password = click.prompt(f"New demo password for {email} (15–128 characters)",
                                    hide_input=True, confirmation_prompt=True)
            if not 15 <= len(password) <= 128:
                raise click.ClickException("Use 15–128 characters. No changes saved.")
            db.execute("INSERT INTO users(email, display_name, role, password_hash) VALUES(?,?,?,?)",
                       (email, name, role, generate_password_hash(password, method="scrypt")))
        for reference, email, date, sku, quantity in orders:
            product = db.execute("SELECT id, price_cents FROM products WHERE sku=?", (sku,)).fetchone()
            if product is None:
                raise click.ClickException("Run seed-demo first. No changes saved.")
            inserted = db.execute(
                "INSERT INTO orders(reference, owner_id, placed_on) "
                "SELECT ?, id, ? FROM users WHERE email=? ON CONFLICT(reference) DO NOTHING",
                (reference, date, email),
            )
            if inserted.rowcount:
                db.execute("INSERT INTO order_items VALUES(?,?,?,?)",
                           (inserted.lastrowid, product["id"], quantity, product["price_cents"]))
    click.echo("Demo accounts and orders ready.")
