"""student crud, search, and relation protection endpoints."""

from flask import Blueprint, jsonify, request

from backend.auth import require_auth
from backend.data import next_id, store
from backend.validators import validate_student_payload

students_bp = Blueprint("students", __name__, url_prefix="/api/students")


def _count_assigned_tasks(student_id: int) -> int:
    """count tasks currently assigned to the given student."""
    return sum(1 for t in store["tasks"] if t["student_id"] == student_id)


def _serialize_student(student: dict) -> dict:
    """return student dict enriched with assigned task count."""
    assigned = _count_assigned_tasks(student["id"])
    return {
        "id": student["id"],
        "nim": student["nim"],
        "nama": student["nama"],
        "email": student["email"],
        "assigned_tasks": assigned,
        "can_delete": assigned == 0,
    }


@students_bp.get("")
@require_auth
def list_students():
    """list students with optional nim, name, or email search."""
    search = request.args.get("search", "").strip().lower()

    filtered = []
    for student in store["students"]:
        if search:
            matches = (
                search in student["nim"].lower()
                or search in student["nama"].lower()
                or search in student["email"].lower()
            )
            if not matches:
                continue
        filtered.append(_serialize_student(student))

    return jsonify({
        "students": filtered,
        "total": len(store["students"]),
        "filtered": len(filtered),
    }), 200


@students_bp.post("")
@require_auth
def create_student():
    """create a new student entity record."""
    payload = request.get_json(silent=True) or {}
    cleaned, error = validate_student_payload(payload, store["students"])
    if error:
        return jsonify({"error": error}), 400

    student = {"id": next_id(store["students"]), **cleaned}
    store["students"].append(student)
    return jsonify({
        "message": "Student created successfully.",
        "student": _serialize_student(student),
    }), 201


@students_bp.put("/<int:student_id>")
@require_auth
def update_student(student_id: int):
    """update an existing student entity record."""
    target = next((s for s in store["students"] if s["id"] == student_id), None)
    if not target:
        return jsonify({"error": "Student not found."}), 404

    payload = request.get_json(silent=True) or {}
    cleaned, error = validate_student_payload(payload, store["students"], exclude_id=student_id)
    if error:
        return jsonify({"error": error}), 400

    target.update(cleaned)
    return jsonify({
        "message": "Student updated successfully.",
        "student": _serialize_student(target),
    }), 200


@students_bp.delete("/<int:student_id>")
@require_auth
def delete_student(student_id: int):
    """delete a student only if no tasks are assigned to them."""
    index = next((i for i, s in enumerate(store["students"]) if s["id"] == student_id), None)
    if index is None:
        return jsonify({"error": "Student not found."}), 404

    assigned = _count_assigned_tasks(student_id)
    if assigned > 0:
        return jsonify({
            "error": "Cannot delete student because they are still assigned to active tasks."
        }), 409

    store["students"].pop(index)
    return jsonify({"message": "Student deleted successfully."}), 200
