import logging
import os

from dotenv import load_dotenv
from flask import Flask, abort, send_from_directory

from backend.db import DatabaseError, init_database
from backend.routes import api as api_blueprint

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# Load environment variables
load_dotenv()


def create_app() -> Flask:
    # ===========================
    # BASE DIRECTORY (IMPORTANT FIX)
    # ===========================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # ===========================
    # FLASK APP INITIALIZATION
    # ===========================
    app = Flask(__name__, static_folder=BASE_DIR)

    # ===========================
    # CONFIG
    # ===========================
    db_path = os.path.join(BASE_DIR, "database.db")
    db_path = os.environ.get("DATABASE_PATH", db_path)

    secret_key = os.environ.get("FLASK_SECRET_KEY")
    if not secret_key:
        secret_key = os.urandom(24).hex()
        logging.warning(
            "FLASK_SECRET_KEY is not set; using a temporary key (sessions will not persist)."
        )

    app.config.update(
        DATABASE_PATH=db_path,
        CORS_ALLOW_ORIGIN=os.environ.get("CORS_ALLOW_ORIGIN", "*"),
        LOGIN_USERNAME=os.environ.get("LOGIN_USERNAME", ""),
        LOGIN_PASSWORD=os.environ.get("LOGIN_PASSWORD", ""),
        SECRET_KEY=secret_key,
    )

    # ===========================
    # DATABASE INIT
    # ===========================
    try:
        init_database(app.config["DATABASE_PATH"])
        logging.info("SQLite initialized/verified.")
    except DatabaseError as e:
        logging.exception("Database initialization failed: %s", e)

    # ===========================
    # API ROUTES
    # ===========================
    app.register_blueprint(api_blueprint)

    # ===========================
    # FRONTEND ROUTE (FIXED)
    # ===========================
    @app.route("/")
    def index():
        return send_from_directory(BASE_DIR, "index.html")

    # ===========================
    # STATIC FILES ROUTE (FIXED)
    # ===========================
    ALLOWED_STATIC_EXTENSIONS = {
        ".html",
        ".css",
        ".js",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".webp",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".map",
    }

    @app.route("/<path:filename>")
    def static_files(filename: str):
        if filename.startswith("api/"):
            abort(404)

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_STATIC_EXTENSIONS:
            abort(404)

        return send_from_directory(BASE_DIR, filename)

    return app


app = create_app()


# ===========================
# LOCAL RUN
# ===========================
if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port)
