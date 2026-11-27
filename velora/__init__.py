import os
from pathlib import Path

from flask import Flask

from . import accounts, catalog, db
from .seed import seed_accounts
from .throttle import MinuteBudget


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=Path(app.instance_path) / "catalog.sqlite")
    app.config.update(SESSION_COOKIE_SECURE=os.environ.get("VELORA_HTTPS") == "1",
                      MAX_CONTENT_LENGTH=32 * 1024)
    if config:
        app.config.update(config)
    app.extensions["login_attempts"] = MinuteBudget(10)
    app.extensions["anonymous_sessions"] = MinuteBudget(20)
    app.url_map.converters["order_id"] = accounts.OrderIDConverter
    db.init_app(app)
    app.cli.add_command(seed_accounts)
    app.register_blueprint(catalog.bp)
    app.register_blueprint(accounts.bp)

    @app.template_filter("euros")
    def euros(cents):
        return f"€{cents // 100}.{cents % 100:02d}"

    return app
