import logging
import os
import sqlite3
from typing import Optional


log = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Create a new SQLite connection per request.
    Using WAL + busy_timeout improves multi-user behavior.
    """
    try:
        # check_same_thread=False lets different threads/workers use connections.
        conn = sqlite3.connect(
            db_path,
            timeout=10,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        # Helps concurrent reads/writes in basic multi-user scenarios.
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn
    except sqlite3.Error as e:
        raise DatabaseError(str(e)) from e


def init_database(db_path: str) -> None:
    """
    Initialize tables on first run.
    If DB can't be created/initialized, raise DatabaseError.
    """
    try:
        # Ensure directory exists (Render deploys into a writable folder).
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        conn = get_connection(db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS health_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    village TEXT NOT NULL,
                    diarrhea INTEGER NOT NULL,
                    fever INTEGER NOT NULL,
                    rainfall TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    date TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        log.exception("Failed to initialize database: %s", e)
        raise DatabaseError(str(e)) from e


def healthcheck(db_path: str) -> bool:
    """Used for lightweight readiness checks."""
    try:
        conn = get_connection(db_path)
        conn.execute("SELECT 1")
        conn.close()
        return True
    except Exception:
        return False

