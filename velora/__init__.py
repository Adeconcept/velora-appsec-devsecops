from pathlib import Path

from flask import Flask

from . import catalog, db


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=Path(app.instance_path) / "catalog.sqlite")
    if config:
        app.config.update(config)
    db.init_app(app)
    app.register_blueprint(catalog.bp)

    @app.template_filter("euros")
    def euros(cents):
        return f"€{cents // 100}.{cents % 100:02d}"

    return app
