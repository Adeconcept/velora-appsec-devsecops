import sqlite3

import pytest
from markupsafe import escape

from velora import create_app
from velora.db import connection


@pytest.fixture
def app(tmp_path):
    app = create_app({"DATABASE": tmp_path / "catalog.sqlite", "TESTING": True})
    for command in ("init-db", "seed-demo"):
        result = app.test_cli_runner().invoke(args=[command])
        assert result.exit_code == 0, result.exception
    return app


def test_setup_preserves_edits(app):
    with app.app_context(), connection() as db:
        db.execute("UPDATE products SET price_cents = 700 WHERE sku = 'VL-101'")
    for command in ("init-db", "seed-demo"):
        assert app.test_cli_runner().invoke(args=[command]).exit_code == 0
    with app.app_context():
        assert connection().execute("SELECT count(*) FROM products").fetchone()[0] == 3
        assert connection().execute("SELECT price_cents FROM products WHERE sku='VL-101'").fetchone()[0] == 700


@pytest.mark.parametrize(("query", "count"), [
    ("", 3), ("   ", 3), ("  NOTEbook ", 1), ("missing", 0),
    ("%", 0), ("_", 0), ("'", 0), ("a" * 100, 0),
])
def test_search(app, query, count):
    response = app.test_client().get("/", query_string={"q": query})
    assert response.status_code == 200
    assert response.data.count(b"<li>") == count
    if not count:
        assert b"No products found" in response.data


def test_search_limit(app):
    response = app.test_client().get("/", query_string={"q": "a" * 101})
    assert response.status_code == 400
    assert b"100 characters or fewer" in response.data


def test_detail(app):
    client = app.test_client()
    assert b'href="/products/1"' in client.get("/").data
    detail = client.get("/products/1")
    assert detail.status_code == 200
    for expected in ["Field Notebook", "€8.50", "VL-101", "dot-grid"]:
        assert expected in detail.get_data(as_text=True)
    assert client.get("/products/999").status_code == 404
    assert client.get(f"/products/{2**63}").status_code == 404


def test_html_contexts(app):
    sample = """<Paper> & "Ink" 'Set'"""
    with app.app_context(), connection() as db:
        db.execute("UPDATE products SET name=?, description=? WHERE id=1", (sample, sample))
    client = app.test_client()
    listing = client.get("/", query_string={"q": sample}).get_data(as_text=True)
    detail = client.get("/products/1").get_data(as_text=True)
    encoded = str(escape(sample))
    assert f'value="{encoded}"' in listing
    assert f">{encoded}</a>" in listing
    assert f"<h1>{encoded}</h1>" in detail and f"<p>{encoded}</p>" in detail
    assert sample not in listing and sample not in detail


@pytest.mark.parametrize("price", [-1, 1.5])
def test_price_constraint(app, price):
    with app.app_context(), pytest.raises(sqlite3.IntegrityError):
        connection().execute("UPDATE products SET price_cents=?", (price,))
