from functools import wraps

from flask import Blueprint, jsonify, request, session

from backend.models.task import (
    create_task,
    delete_task,
    get_task_for_user,
    get_tasks_for_user,
    update_task,
)


tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")
VALID_STATUSES = {"To Do", "In Progress", "Done"}


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return view(*args, **kwargs)

    return wrapped_view


def _task_to_dict(task):
    return {
        "id": task["id"],
        "user_id": task["user_id"],
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "created_at": task["created_at"],
    }


def _json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    return data


@tasks_bp.get("")
@login_required
def list_tasks():
    tasks = get_tasks_for_user(session["user_id"])
    return jsonify([_task_to_dict(task) for task in tasks]), 200


@tasks_bp.get("/<int:task_id>")
@login_required
def get_task(task_id):
    task = get_task_for_user(task_id, session["user_id"])
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(_task_to_dict(task)), 200


@tasks_bp.post("")
@login_required
def add_task():
    data = _json_object()
    if data is None:
        return jsonify({"error": "A JSON object is required"}), 400

    title = data.get("title")
    description = data.get("description")
    status = data.get("status", "To Do")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400
    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string or null"}), 400
    if not isinstance(status, str) or status not in VALID_STATUSES:
        return jsonify({"error": "Status must be To Do, In Progress, or Done"}), 400

    task = create_task(
        session["user_id"],
        title.strip(),
        description,
        status,
    )
    return jsonify(_task_to_dict(task)), 201


@tasks_bp.put("/<int:task_id>")
@login_required
def edit_task(task_id):
    task = get_task_for_user(task_id, session["user_id"])
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    data = _json_object()
    if data is None:
        return jsonify({"error": "A JSON object is required"}), 400
    if not any(field in data for field in ("title", "description", "status")):
        return jsonify({"error": "Provide at least one field to update"}), 400

    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    status = data.get("status", task["status"])
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title must be a non-empty string"}), 400
    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string or null"}), 400
    if not isinstance(status, str) or status not in VALID_STATUSES:
        return jsonify({"error": "Status must be To Do, In Progress, or Done"}), 400

    updated_task = update_task(
        task_id,
        session["user_id"],
        title.strip(),
        description,
        status,
    )
    return jsonify(_task_to_dict(updated_task)), 200


@tasks_bp.delete("/<int:task_id>")
@login_required
def remove_task(task_id):
    if not delete_task(task_id, session["user_id"]):
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task deleted successfully"}), 200
