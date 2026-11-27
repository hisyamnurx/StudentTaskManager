"""dashboard statistics and upcoming deadlines endpoint."""

from flask import Blueprint, jsonify

from backend.auth import require_auth
from backend.data import store
from backend.validators import compute_deadline_status

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("")
@require_auth
def get_dashboard():
    """compute live task statistics, completion rate, deadlines, and entity summaries."""
    tasks = store["tasks"]
    students = store["students"]
    courses = store["courses"]

    student_map = {s["id"]: s for s in students}
    course_map = {c["id"]: c for c in courses}

    total_tasks = len(tasks)
    todo_count = sum(1 for t in tasks if t["status"] == "To Do")
    in_progress_count = sum(1 for t in tasks if t["status"] == "In Progress")
    completed_count = sum(1 for t in tasks if t["status"] == "Completed")

    overdue_count = 0
    due_today_count = 0
    upcoming_items = []

    for task in tasks:
        d_status = compute_deadline_status(task["deadline"], task["status"])
        if d_status == "overdue":
            overdue_count += 1
        elif d_status == "due_today":
            due_today_count += 1

        if task["status"] != "Completed":
            course = course_map.get(task["course_id"], {})
            student = student_map.get(task["student_id"], {})
            upcoming_items.append({
                "id": task["id"],
                "judul": task["judul"],
                "course_name": course.get("nama", "-"),
                "student_name": student.get("nama", "-"),
                "deadline": task["deadline"],
                "deadline_status": d_status,
                "status": task["status"],
                "prioritas": task["prioritas"],
            })

    upcoming_items.sort(key=lambda item: item["deadline"])
    unfinished_tasks = total_tasks - completed_count
    completion_rate = round((completed_count / total_tasks) * 100) if total_tasks > 0 else 0

    active_student_ids = {t["student_id"] for t in tasks}
    total_sks = sum(c["sks"] for c in courses)

    return jsonify({
        "stats": {
            "total_tasks": total_tasks,
            "todo": todo_count,
            "in_progress": in_progress_count,
            "completed": completed_count,
            "overdue": overdue_count,
            "due_today": due_today_count,
            "unfinished_tasks": unfinished_tasks,
            "completion_rate": completion_rate,
        },
        "upcoming_deadlines": upcoming_items[:5],
        "entity_summary": {
            "total_students": len(students),
            "active_students": len(active_student_ids),
            "total_courses": len(courses),
            "total_sks": total_sks,
            "unfinished_tasks": unfinished_tasks,
            "overdue": overdue_count,
            "due_today": due_today_count,
        },
    }), 200
