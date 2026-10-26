import sqlite3

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from backend.models.user import create_user, get_user_by_username


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def _json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    return data


@auth_bp.post("/register")
def register():
    data = _json_object()
    if data is None:
        return jsonify({"error": "A JSON object is required"}), 400

    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Username is required"}), 400
    if not isinstance(password, str) or not password:
        return jsonify({"error": "Password is required"}), 400

    username = username.strip()
    if get_user_by_username(username) is not None:
        return jsonify({"error": "Username is already registered"}), 409

    try:
        user_id = create_user(username, generate_password_hash(password))
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username is already registered"}), 409

    return jsonify({"id": user_id, "username": username}), 201


@auth_bp.post("/login")
def login():
    data = _json_object()
    if data is None:
        return jsonify({"error": "A JSON object is required"}), 400

    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Username is required"}), 400
    if not isinstance(password, str) or not password:
        return jsonify({"error": "Password is required"}), 400

    user = get_user_by_username(username.strip())
    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session.clear()
    session["user_id"] = user["id"]
    return jsonify({"id": user["id"], "username": user["username"]}), 200


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200
