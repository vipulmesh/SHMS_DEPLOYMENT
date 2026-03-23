from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, session

from .db import DatabaseError, get_connection


api = Blueprint("api", __name__)


def _is_authenticated() -> bool:
    return session.get("authenticated") is True


def calculate_risk(diarrhea: int, rainfall: str) -> str:
    # Simple rule-based logic (kept identical to the original app).
    if diarrhea > 10 and rainfall == "High":
        return "High Risk"
    if 5 <= diarrhea <= 10:
        return "Medium Risk"
    return "Safe"


def _require_auth():
    if not _is_authenticated():
        return jsonify(success=False, error="Unauthorized"), 401
    return None


@api.after_request
def add_cors_headers(response):
    """
    Basic CORS support for deployments where the frontend is separate.
    Note: for cookie-based auth across origins, you must configure credentials
    properly; this app is primarily intended for same-origin hosting.
    """
    allow_origin = current_app.config.get("CORS_ALLOW_ORIGIN", "*")
    response.headers.setdefault("Access-Control-Allow-Origin", allow_origin)
    response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type")
    response.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


@api.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 204

    try:
        payload = request.get_json(silent=True) or {}
        username = payload.get("username", "")
        password = payload.get("password", "")

        expected_username = current_app.config.get("LOGIN_USERNAME")
        expected_password = current_app.config.get("LOGIN_PASSWORD")

        if not expected_username or not expected_password:
            # Misconfiguration in production.
            return jsonify(success=False, error="Server login not configured"), 500

        if username == expected_username and password == expected_password:
            session["authenticated"] = True
            return jsonify(success=True), 200

        return jsonify(success=False, error="Invalid credentials"), 401
    except Exception:
        return jsonify(success=False, error="Login failed"), 500


@api.route("/api/logout", methods=["POST", "OPTIONS"])
def logout():
    if request.method == "OPTIONS":
        return "", 204
    session.clear()
    return jsonify(success=True), 200


@api.route("/api/me", methods=["GET"])
def me():
    if not _is_authenticated():
        return jsonify(authenticated=False), 401
    return jsonify(authenticated=True), 200


@api.route("/submit", methods=["POST", "OPTIONS"])
def submit_data():
    if request.method == "OPTIONS":
        return "", 204

    auth_err = _require_auth()
    if auth_err:
        return auth_err

    try:
        data = request.get_json(silent=True) or {}
        village = (data.get("village") or "").strip()
        if not village:
            return jsonify(success=False, error="Missing village"), 400

        diarrhea = int(data.get("diarrhea"))
        fever = int(data.get("fever"))
        rainfall = data.get("rainfall")

        rainfall = str(rainfall) if rainfall is not None else ""
        rainfall = rainfall.strip().capitalize()
        if rainfall not in {"Low", "Medium", "High"}:
            return jsonify(success=False, error="Invalid rainfall"), 400

        if diarrhea < 0 or fever < 0:
            return jsonify(success=False, error="Invalid case counts"), 400

        risk = calculate_risk(diarrhea, rainfall)
        date = datetime.now().strftime("%Y-%m-%d")

        db_path = current_app.config["DATABASE_PATH"]
        conn = get_connection(db_path)
        try:
            conn.execute(
                """
                INSERT INTO health_data
                (village, diarrhea, fever, rainfall, risk, date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (village, diarrhea, fever, rainfall, risk, date),
            )
            conn.commit()
        finally:
            conn.close()

        return jsonify(success=True, risk=risk), 201
    except (ValueError, TypeError):
        return jsonify(success=False, error="Invalid input types"), 400
    except DatabaseError as e:
        return jsonify(success=False, error=f"Database error: {e}"), 500
    except Exception:
        return jsonify(success=False, error="Submit failed"), 500


@api.route("/data", methods=["GET"])
def get_data():
    auth_err = _require_auth()
    if auth_err:
        return auth_err

    try:
        db_path = current_app.config["DATABASE_PATH"]
        conn = get_connection(db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM health_data ORDER BY id DESC"
            ).fetchall()
        finally:
            conn.close()

        result = []
        for r in rows:
            result.append(
                {
                    "id": r["id"],
                    "village": r["village"],
                    "diarrhea": r["diarrhea"],
                    "fever": r["fever"],
                    "rainfall": r["rainfall"],
                    "risk": r["risk"],
                    "date": r["date"],
                }
            )
        return jsonify(result), 200
    except DatabaseError as e:
        return jsonify(success=False, error=f"Database error: {e}"), 500
    except Exception:
        return jsonify(success=False, error="Fetch failed"), 500

