"""course crud, search, sks filtering, and relation protection endpoints."""

from flask import Blueprint, jsonify, request

from backend.auth import require_auth
from backend.data import next_id, store
from backend.validators import validate_course_payload

courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")


def _count_linked_tasks(course_id: int) -> int:
    """count tasks currently assigned to the given course."""
    return sum(1 for t in store["tasks"] if t["course_id"] == course_id)


def _serialize_course(course: dict) -> dict:
    """return course dict enriched with linked task count."""
    linked = _count_linked_tasks(course["id"])
    return {
        "id": course["id"],
        "kode": course["kode"],
        "nama": course["nama"],
        "sks": course["sks"],
        "linked_tasks": linked,
        "can_delete": linked == 0,
    }


@courses_bp.get("")
@require_auth
def list_courses():
    """list courses with optional code/name search and sks filter."""
    search = request.args.get("search", "").strip().lower()
    sks_filter = request.args.get("sks", "").strip()

    filtered = []
    for course in store["courses"]:
        if search and search not in course["kode"].lower() and search not in course["nama"].lower():
            continue
        if sks_filter:
            try:
                if course["sks"] != int(sks_filter):
                    continue
            except ValueError:
                continue
        filtered.append(_serialize_course(course))

    total_sks = sum(c["sks"] for c in store["courses"])
    return jsonify({
        "courses": filtered,
        "total": len(store["courses"]),
        "total_sks": total_sks,
        "filtered": len(filtered),
    }), 200


@courses_bp.post("")
@require_auth
def create_course():
    """create a new course record."""
    payload = request.get_json(silent=True) or {}
    cleaned, error = validate_course_payload(payload, store["courses"])
    if error:
        return jsonify({"error": error}), 400

    course = {"id": next_id(store["courses"]), **cleaned}
    store["courses"].append(course)
    return jsonify({
        "message": "Course created successfully.",
        "course": _serialize_course(course),
    }), 201


@courses_bp.put("/<int:course_id>")
@require_auth
def update_course(course_id: int):
    """update an existing course record."""
    target = next((c for c in store["courses"] if c["id"] == course_id), None)
    if not target:
        return jsonify({"error": "Course not found."}), 404

    payload = request.get_json(silent=True) or {}
    cleaned, error = validate_course_payload(payload, store["courses"], exclude_id=course_id)
    if error:
        return jsonify({"error": error}), 400

    target.update(cleaned)
    return jsonify({
        "message": "Course updated successfully.",
        "course": _serialize_course(target),
    }), 200


@courses_bp.delete("/<int:course_id>")
@require_auth
def delete_course(course_id: int):
    """delete a course only if no tasks are linked to it."""
    index = next((i for i, c in enumerate(store["courses"]) if c["id"] == course_id), None)
    if index is None:
        return jsonify({"error": "Course not found."}), 404

    linked = _count_linked_tasks(course_id)
    if linked > 0:
        return jsonify({
            "error": "Cannot delete course because it is still linked to active tasks."
        }), 409

    store["courses"].pop(index)
    return jsonify({"message": "Course deleted successfully."}), 200
