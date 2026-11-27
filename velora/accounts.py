from flask import abort, g, redirect, render_template, request, url_for

from werkzeug.routing import IntegerConverter

from .access import bp
from .db import connection


class OrderIDConverter(IntegerConverter):
    # Bound the decimal representation before Python converts it to an integer.
    regex = r"[0-9]{1,19}"


@bp.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        name = request.form.get("display_name", "").strip()
        if not 1 <= len(name) <= 80:
            return render_template("profile.html", error="Enter a name of 1–80 characters."), 400
        with connection() as db:
            db.execute("UPDATE users SET display_name=? WHERE id=?", (name, g.identity["user_id"]))
        return redirect(url_for("account.profile"), code=303)
    return render_template("profile.html")


@bp.get("/orders")
def orders():
    rows = connection().execute("SELECT id, reference, placed_on, status FROM orders "
                                "WHERE owner_id=? ORDER BY id DESC", (g.identity["user_id"],))
    return render_template("orders.html", rows=rows)


@bp.get("/orders/<order_id:order_id>")
def order(order_id):
    if order_id > 2**63 - 1:
        abort(404)
    db = connection()
    owned = db.execute("SELECT id, reference, placed_on, status FROM orders WHERE id=? AND owner_id=?",
                       (order_id, g.identity["user_id"])).fetchone()
    if owned is None:
        abort(404)
    items = db.execute("SELECT p.name, i.quantity, i.unit_cents FROM order_items i "
                       "JOIN products p ON p.id=i.product_id WHERE i.order_id=?", (owned["id"],))
    return render_template("order.html", order=owned, items=items)


@bp.get("/admin/orders")
def fulfillment():
    rows = connection().execute("SELECT id, reference, placed_on, status FROM orders ORDER BY id DESC")
    return render_template("orders.html", rows=rows, admin=True)


@bp.post("/admin/orders/<order_id:order_id>/ship")
def ship(order_id):
    if order_id > 2**63 - 1:
        abort(404)
    with connection() as db:
        updated = db.execute("UPDATE orders SET status='shipped' WHERE id=? AND status='processing'", (order_id,))
        if not updated.rowcount:
            exists = db.execute("SELECT 1 FROM orders WHERE id=?", (order_id,)).fetchone()
            abort(409 if exists else 404)
    return redirect(url_for("account.fulfillment"), code=303)
