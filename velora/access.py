"""Session lifecycle and the access policy for every account endpoint."""
import hashlib
import secrets
import time

from flask import Blueprint, abort, current_app, g, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import connection

bp = Blueprint("account", __name__)
COOKIE = "velora_session"
IDLE = 15 * 60
LIFETIME = 8 * 60 * 60
DUMMY_HASH = generate_password_hash(secrets.token_urlsafe(), method="scrypt")
POLICY = {
    "account.login": {"guest", "customer", "admin"},
    "account.logout": {"customer", "admin"},
    "account.profile": {"customer", "admin"},
    "account.orders": {"customer"},
    "account.order": {"customer"},
    "account.fulfillment": {"admin"},
    "account.ship": {"admin"},
}


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


@bp.before_request
def check_access():
    token = request.cookies.get(COOKIE, "")
    now = int(time.time())
    db = connection()
    g.identity = db.execute(
        "SELECT s.*, u.role, u.email, u.display_name FROM sessions s "
        "LEFT JOIN users u ON u.id=s.user_id "
        "WHERE s.token_hash=? AND s.expires>? AND s.last_seen>?",
        (digest(token), now, now - IDLE),
    ).fetchone()
    role = g.identity["role"] if g.identity and g.identity["user_id"] else "guest"
    if role not in POLICY.get(request.endpoint, set()):
        abort(401 if role == "guest" else 403)
    if request.method == "POST":
        supplied = request.form.get("csrf", "").encode()
        if not g.identity or not secrets.compare_digest(g.identity["csrf"].encode(), supplied):
            abort(400)
    if g.identity:
        with db:
            db.execute("UPDATE sessions SET last_seen=? WHERE token_hash=?", (now, digest(token)))


@bp.after_request
def private_headers(response):
    response.cache_control.no_store = True
    if hasattr(g, "new_token"):
        response.set_cookie(COOKIE, g.new_token, httponly=True, samesite="Strict",
                            secure=current_app.config["SESSION_COOKIE_SECURE"], path="/")
    return response


def start_session(user_id):
    now = int(time.time())
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    with connection() as db:
        db.execute("DELETE FROM sessions WHERE expires<=? OR last_seen<=?", (now, now - IDLE))
        if g.identity:
            db.execute("DELETE FROM sessions WHERE token_hash=?", (g.identity["token_hash"],))
        db.execute("INSERT INTO sessions VALUES(?,?,?,?,?)",
                   (digest(token), user_id, csrf, now + LIFETIME, now))
    g.new_token = token
    return csrf


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.identity and g.identity["user_id"]:
        return redirect(url_for("account.profile"))
    if request.method == "GET":
        csrf = g.identity["csrf"] if g.identity else start_session(None)
        return render_template("login.html", csrf=csrf)
    user = connection().execute("SELECT id, password_hash FROM users WHERE email=?",
                                (request.form.get("email", "").strip(),)).fetchone()
    password = request.form.get("password", "")
    valid = check_password_hash(user["password_hash"] if user else DUMMY_HASH, password)
    if not user or not valid:
        return render_template("login.html", csrf=g.identity["csrf"], error="Invalid email or password."), 401
    start_session(user["id"])
    return redirect(url_for("account.profile"), code=303)


@bp.post("/logout")
def logout():
    with connection() as db:
        db.execute("DELETE FROM sessions WHERE token_hash=?", (g.identity["token_hash"],))
    response = redirect(url_for("catalog.index"), code=303)
    response.delete_cookie(COOKIE, path="/", httponly=True, samesite="Strict",
                           secure=current_app.config["SESSION_COOKIE_SECURE"])
    return response
