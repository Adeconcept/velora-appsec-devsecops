import hashlib
import re
import secrets
import shutil
import sqlite3

import pytest
from werkzeug.security import check_password_hash

from velora import create_app
from velora.access import COOKIE
from velora.db import connection


@pytest.fixture(scope="module")
def seeded(tmp_path_factory):
    path = tmp_path_factory.mktemp("seed") / "catalog.sqlite"
    app = create_app({"TESTING": True, "DATABASE": path})
    passwords = {name: secrets.token_urlsafe(24) for name in ("avery", "morgan", "ops")}
    runner = app.test_cli_runner()
    for command in ("init-db", "seed-demo"):
        assert runner.invoke(args=[command]).exit_code == 0
    answers = "".join(f"{pw}\n{pw}\n" for pw in passwords.values())
    result = runner.invoke(args=["seed-accounts"], input=answers)
    assert result.exit_code == 0, result.exception
    return path, passwords


@pytest.fixture
def app(tmp_path, seeded):
    path = tmp_path / "catalog.sqlite"
    shutil.copyfile(seeded[0], path)
    return create_app({"TESTING": True, "DATABASE": path})


def csrf(response):
    return re.search(rb'name="csrf" value="([^"]+)"', response.data)[1].decode()


def sign_in(app, name, seeded):
    client = app.test_client()
    token = csrf(client.get("/login"))
    response = client.post("/login", data={"email": f"{name}@example.test", "password": seeded[1][name], "csrf": token})
    assert response.status_code == 303
    return client, csrf(client.get("/profile"))


def test_storage_and_idempotent_seed(app, seeded):
    assert app.test_cli_runner().invoke(args=["seed-accounts"]).exit_code == 0
    with app.app_context():
        users = connection().execute("SELECT * FROM users").fetchall()
        assert len(users) == 3
        for user in users:
            assert user["password_hash"].startswith("scrypt:")
            assert check_password_hash(user["password_hash"], seeded[1][user["email"].split("@")[0]])
        assert connection().execute("SELECT count(*) FROM orders").fetchone()[0] == 2
        assert connection().execute("SELECT count(*) FROM order_items").fetchone()[0] == 2
        with pytest.raises(sqlite3.IntegrityError):
            connection().execute("UPDATE orders SET owner_id=-1")


@pytest.mark.parametrize("email", ["avery@example.test", "unknown@example.test"])
def test_failed_login(app, email):
    client = app.test_client()
    token = csrf(client.get("/login"))
    response = client.post("/login", data={"email": email, "password": "incorrect", "csrf": token})
    assert response.status_code == 401 and b"Invalid email or password" in response.data
    assert client.get("/profile").status_code == 401


@pytest.mark.parametrize(("method", "url"), [
    ("get", "/profile"), ("post", "/profile"), ("get", "/orders"), ("get", "/orders/1"),
    ("get", "/admin/orders"), ("post", "/admin/orders/1/ship"), ("post", "/logout"),
])
def test_logged_out_access(app, method, url):
    assert getattr(app.test_client(), method)(url).status_code == 401


@pytest.mark.parametrize(("name", "own", "other", "total"), [
    ("avery", 1, 2, "€17.00"), ("morgan", 2, 1, "€24.00"),
])
def test_customer_boundary(app, seeded, name, own, other, total):
    client, token = sign_in(app, name, seeded)
    listing = client.get("/orders", query_string={"owner_id": other}).data
    assert f"VC-100{own}".encode() in listing and f"VC-100{other}".encode() not in listing
    assert total in client.get(f"/orders/{own}").get_data(as_text=True)
    denied = client.get(f"/orders/{other}")
    absent = client.get("/orders/999")
    assert denied.status_code == absent.status_code == 404 and denied.data == absent.data
    assert client.get("/admin/orders").status_code == 403
    assert client.post(f"/admin/orders/{own}/ship", data={"csrf": token, "role": "admin"}).status_code == 403
    response = client.post("/profile", data={"csrf": token, "display_name": "A & B",
                                             "user_id": other, "role": "admin", "email": "x@example.test"})
    assert response.status_code == 303
    assert b"A &amp; B" in client.get("/profile").data
    with app.app_context():
        rows = connection().execute("SELECT * FROM users ORDER BY id").fetchall()
        assert rows[own-1]["email"] == f"{name}@example.test" and rows[own-1]["role"] == "customer"
        assert rows[other-1]["display_name"] != "A & B"
        assert connection().execute("SELECT status FROM orders WHERE id=?", (own,)).fetchone()[0] == "processing"


def test_admin_scope_and_transition(app, seeded):
    admin, token = sign_in(app, "ops", seeded)
    customer, _ = sign_in(app, "avery", seeded)
    queue = admin.get("/admin/orders")
    assert queue.status_code == 200 and all(ref in queue.data for ref in (b"VC-1001", b"VC-1002"))
    assert admin.get("/orders/1").status_code == admin.get("/orders").status_code == 403
    assert admin.post("/admin/orders/1/ship", data={"csrf": token, "owner_id": 2}).status_code == 303
    assert b"shipped" in customer.get("/orders/1").data
    assert admin.post("/admin/orders/1/ship", data={"csrf": token}).status_code == 409
    assert admin.post("/admin/orders/999/ship", data={"csrf": token}).status_code == 404


@pytest.mark.parametrize("foreign", [False, True])
def test_csrf_for_all_writes(app, seeded, foreign):
    client = app.test_client()
    client.get("/login")
    data = {"csrf": csrf(app.test_client().get("/login"))} if foreign else {}
    assert client.post("/login", data={**data, "email": "ops@example.test", "password": seeded[1]["ops"]}).status_code == 400
    assert client.get("/profile").status_code == 401
    admin, _ = sign_in(app, "ops", seeded)
    for url in ("/profile", "/admin/orders/1/ship", "/logout"):
        assert admin.post(url, data={**data, "display_name": "Changed"}).status_code == 400
    assert b"Operations" in admin.get("/profile").data
    with app.app_context():
        assert connection().execute("SELECT status FROM orders WHERE id=1").fetchone()[0] == "processing"


def test_session_rotation_and_revocation(app, seeded):
    client = app.test_client()
    prelogin = client.get("/login")
    initial = client.get_cookie(COOKIE).value
    assert "HttpOnly" in prelogin.headers["Set-Cookie"] and "SameSite=Strict" in prelogin.headers["Set-Cookie"]
    assert client.post("/login", data={"csrf": csrf(prelogin), "email": "avery@example.test",
                                       "password": seeded[1]["avery"]}).status_code == 303
    current = client.get_cookie(COOKIE).value
    assert current != initial
    replay = app.test_client()
    replay.set_cookie(COOKIE, initial)
    assert replay.get("/profile").status_code == 401
    profile = client.get("/profile")
    assert profile.cache_control.no_store
    assert client.post("/logout", data={"csrf": csrf(profile)}).status_code == 303
    replay.set_cookie(COOKIE, current)
    assert replay.get("/profile").status_code == 401


@pytest.mark.parametrize("field", ["last_seen", "expires"])
def test_expiration(app, seeded, field):
    client, _ = sign_in(app, "avery", seeded)
    token = client.get_cookie(COOKIE).value
    with app.app_context(), connection() as db:
        assert db.execute("SELECT token_hash FROM sessions").fetchone()[0] == hashlib.sha256(token.encode()).hexdigest()
        sql = {"last_seen": "UPDATE sessions SET last_seen=0", "expires": "UPDATE sessions SET expires=0"}
        db.execute(sql[field])
    assert client.get("/orders").status_code == 401


def test_https_cookie_configuration(app):
    app.config["SESSION_COOKIE_SECURE"] = True
    response = app.test_client().get("/login", base_url="https://localhost")
    assert "Secure;" in response.headers["Set-Cookie"]
