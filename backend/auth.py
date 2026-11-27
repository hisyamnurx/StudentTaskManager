"""authentication endpoints, password hashing, and in-memory session guard."""

import secrets
from functools import wraps
from flask import Blueprint, jsonify, make_response, request
from werkzeug.security import check_password_hash, generate_password_hash

from backend.data import next_id, store
from backend.validators import validate_register_payload

SESSION_COOKIE_NAME = "stm_session"
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def get_session_token():
    """extract session token from authorization header or session cookie."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token:
            return token
    return request.cookies.get(SESSION_COOKIE_NAME)


def get_current_user():
    """return current authenticated user dict or none."""
    token = get_session_token()
    if not token:
        return None
    return store["sessions"].get(token)


def require_auth(view_func):
    """protect api routes that require a valid active session."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "Authentication required."}), 401
        return view_func(*args, **kwargs)

    return wrapped


@auth_bp.post("/register")
def register():
    """register a new user account in memory with hashed password."""
    payload = request.get_json(silent=True) or {}
    cleaned, error = validate_register_payload(payload, store["accounts"])
    if error:
        return jsonify({"error": error}), 400

    account = {
        "id": next_id(store["accounts"]),
        "full_name": cleaned["full_name"],
        "nim": cleaned["nim"],
        "email": cleaned["email"],
        "password_hash": generate_password_hash(cleaned["password"]),
    }
    store["accounts"].append(account)

    return jsonify({
        "message": "Account created successfully. Please sign in.",
        "user": {
            "id": account["id"],
            "full_name": account["full_name"],
            "nim": account["nim"],
            "email": account["email"],
        },
    }), 201


@auth_bp.post("/login")
def login():
    """authenticate user by email or nim and create an in-memory session."""
    payload = request.get_json(silent=True) or {}
    identifier = str(payload.get("identifier", "")).strip()
    password = str(payload.get("password", ""))

    if not identifier or not password:
        return jsonify({"error": "Email / NIM and password are required."}), 400

    matched = None
    lower_id = identifier.lower()
    for account in store["accounts"]:
        if account["email"].lower() == lower_id or account["nim"] == identifier:
            matched = account
            break

    if not matched or not check_password_hash(matched["password_hash"], password):
        return jsonify({"error": "Invalid credentials."}), 401

    token = secrets.token_urlsafe(32)
    user_session = {
        "account_id": matched["id"],
        "full_name": matched["full_name"],
        "nim": matched["nim"],
        "email": matched["email"],
    }
    store["sessions"][token] = user_session

    response = make_response(jsonify({
        "message": "Signed in successfully.",
        "token": token,
        "user": user_session,
    }), 200)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        samesite="Lax",
        path="/",
    )
    return response


@auth_bp.post("/logout")
def logout():
    """remove the active session token and clear cookie."""
    token = get_session_token()
    if token:
        store["sessions"].pop(token, None)

    response = make_response(jsonify({"message": "Signed out successfully."}), 200)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return response


@auth_bp.get("/me")
@require_auth
def me():
    """return currently authenticated user profile."""
    return jsonify({"user": get_current_user()}), 200
