from flask import Blueprint, abort, render_template, request

from .db import connection

bp = Blueprint("catalog", __name__)


@bp.get("/")
def index():
    query = request.args.get("q", "").strip()
    if len(query) > 100:
        return render_template("catalog.html", query="", error="Enter 100 characters or fewer."), 400
    products = connection().execute(
        "SELECT id, sku, name, price_cents FROM products "
        "WHERE instr(lower(name), lower(?)) > 0 ORDER BY name, id", (query,)
    ).fetchall()
    return render_template("catalog.html", products=products, query=query)


@bp.get("/products/<int:product_id>")
def detail(product_id):
    if product_id > 2**63 - 1:
        abort(404)
    product = connection().execute(
        "SELECT sku, name, description, price_cents FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    if product is None:
        abort(404)
    return render_template("product.html", product=product)
