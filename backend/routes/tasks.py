"""task crud, filtering, sorting, and assignment endpoints."""

from flask import Blueprint, jsonify, request

from backend.auth import require_auth
from backend.data import next_id, store
from backend.validators import compute_deadline_status, validate_task_payload

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


def _serialize_task(task: dict, student_map: dict, course_map: dict) -> dict:
    """enrich task dict with related student, course, and deadline status."""
    student = student_map.get(task["student_id"], {})
    course = course_map.get(task["course_id"], {})
    return {
        "id": task["id"],
        "judul": task["judul"],
        "deskripsi": task["deskripsi"],
        "deadline": task["deadline"],
        "prioritas": task["prioritas"],
        "status": task["status"],
        "student_id": task["student_id"],
        "course_id": task["course_id"],
        "student_name": student.get("nama", "-"),
        "student_nim": student.get("nim", "-"),
        "course_code": course.get("kode", "-"),
        "course_name": course.get("nama", "-"),
        "deadline_status": compute_deadline_status(task["deadline"], task["status"]),
    }


@tasks_bp.get("")
@require_auth
def list_tasks():
    """list tasks with optional title search, filters, and deadline sorting."""
    search = request.args.get("search", "").strip().lower()
    student_id = request.args.get("student_id", "").strip()
    course_id = request.args.get("course_id", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    sort_order = request.args.get("sort", "asc").strip().lower()

    student_map = {s["id"]: s for s in store["students"]}
    course_map = {c["id"]: c for c in store["courses"]}

    filtered = []
    for task in store["tasks"]:
        if search and search not in task["judul"].lower():
            continue
        if student_id:
            try:
                if task["student_id"] != int(student_id):
                    continue
            except ValueError:
                continue
        if course_id:
            try:
                if task["course_id"] != int(course_id):
                    continue
            except ValueError:
                continue
        if status and task["status"] != status:
            continue
        if priority and task["prioritas"] != priority:
            continue
        filtered.append(_serialize_task(task, student_map, course_map))

    filtered.sort(key=lambda item: item["deadline"], reverse=(sort_order == "desc"))

    return jsonify({
        "tasks": filtered,
        "total": len(store["tasks"]),
        "filtered": len(filtered),
    }), 200


@tasks_bp.post("")
@require_auth
def create_task():
    """create a new task assigned to a valid student and course."""
    payload = request.get_json(silent=True) or {}
    cleaned, error = validate_task_payload(payload, store["students"], store["courses"])
    if error:
        return jsonify({"error": error}), 400

    task = {"id": next_id(store["tasks"]), **cleaned}
    store["tasks"].append(task)

    student_map = {s["id"]: s for s in store["students"]}
    course_map = {c["id"]: c for c in store["courses"]}
    return jsonify({
        "message": "Task created successfully.",
        "task": _serialize_task(task, student_map, course_map),
    }), 201


@tasks_bp.put("/<int:task_id>")
@require_auth
def update_task(task_id: int):
    """update an existing task and validate its relations."""
    target = next((t for t in store["tasks"] if t["id"] == task_id), None)
    if not target:
        return jsonify({"error": "Task not found."}), 404

    payload = request.get_json(silent=True) or {}
    cleaned, error = validate_task_payload(payload, store["students"], store["courses"])
    if error:
        return jsonify({"error": error}), 400

    target.update(cleaned)
    student_map = {s["id"]: s for s in store["students"]}
    course_map = {c["id"]: c for c in store["courses"]}
    return jsonify({
        "message": "Task updated successfully.",
        "task": _serialize_task(target, student_map, course_map),
    }), 200


@tasks_bp.delete("/<int:task_id>")
@require_auth
def delete_task(task_id: int):
    """delete a task by id."""
    index = next((i for i, t in enumerate(store["tasks"]) if t["id"] == task_id), None)
    if index is None:
        return jsonify({"error": "Task not found."}), 404

    store["tasks"].pop(index)
    return jsonify({"message": "Task deleted successfully."}), 200
