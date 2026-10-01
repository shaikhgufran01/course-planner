import os
from pathlib import Path

from flask import Flask, abort, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder=str(BASE_DIR / "static"),
        static_url_path="/static",
        template_folder=str(BASE_DIR / "templates"),
    )
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, "planner.db")
    db_url = os.environ.get("DATABASE_URL", f"sqlite:///{db_path}")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from .routes import bp as api_bp
    app.register_blueprint(api_bp)

    from . import models  # noqa: F401  (registers tables with SQLAlchemy)

    with app.app_context():
        db.create_all()
        from .seed import seed
        seed()

    # --- serve the built Vue SPA for every non-API route ---
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path):
        if path.startswith("api/"):
            abort(404)
        candidate = BASE_DIR / "static" / path
        if path and candidate.is_file():
            return send_from_directory(BASE_DIR / "static", path)
        index = BASE_DIR / "templates" / "index.html"
        if not index.exists():
            return (
                "Frontend not built yet. Run `cd frontend && npm run build`, "
                "then reload.",
                200,
            )
        # served as a static file (not render_template) so Jinja never
        # parses the compiled bundle's own minified content
        return send_from_directory(BASE_DIR / "templates", "index.html")

    return app
