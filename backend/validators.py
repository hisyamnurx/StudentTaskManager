"""input validation and deadline calculation helpers."""

import re
from datetime import date

VALID_PRIORITIES = ("Low", "Medium", "High")
VALID_STATUSES = ("To Do", "In Progress", "Completed")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(value: str) -> bool:
    """check basic email address syntax."""
    return bool(EMAIL_PATTERN.match(value))


def is_valid_iso_date(value: str) -> bool:
    """verify that string represents a valid yyyy-mm-dd date."""
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def compute_deadline_status(deadline_str: str, status: str) -> str:
    """classify task deadline relative to today when not completed."""
    if status == "Completed":
        return "completed"
    try:
        due = date.fromisoformat(deadline_str)
    except (TypeError, ValueError):
        return "upcoming"
    today = date.today()
    if due < today:
        return "overdue"
    if due == today:
        return "due_today"
    return "upcoming"


def validate_register_payload(payload: dict, accounts: list) -> tuple:
    """validate registration input and check duplicate email or nim."""
    full_name = str(payload.get("full_name", "")).strip()
    nim = str(payload.get("nim", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    confirm_password = str(payload.get("confirm_password", ""))

    if not full_name or not nim or not email or not password or not confirm_password:
        return None, "All fields are required."
    if not nim.isdigit() or len(nim) < 5:
        return None, "NIM must contain at least 5 digits."
    if not is_valid_email(email):
        return None, "Please enter a valid email address."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."
    if password != confirm_password:
        return None, "Passwords do not match."

    for acc in accounts:
        if acc["email"].lower() == email:
            return None, "Email is already registered."
        if acc["nim"] == nim:
            return None, "NIM is already registered."

    return {
        "full_name": full_name,
        "nim": nim,
        "email": email,
        "password": password,
    }, None


def validate_student_payload(payload: dict, students: list, exclude_id=None) -> tuple:
    """validate student entity fields and uniqueness of nim and email."""
    nim = str(payload.get("nim", "")).strip()
    nama = str(payload.get("nama", "")).strip()
    email = str(payload.get("email", "")).strip().lower()

    if not nim or not nama or not email:
        return None, "NIM, full name, and email are required."
    if not nim.isdigit() or len(nim) < 5:
        return None, "NIM must contain at least 5 digits."
    if not is_valid_email(email):
        return None, "Please enter a valid email address."

    for student in students:
        if exclude_id is not None and student["id"] == exclude_id:
            continue
        if student["nim"] == nim:
            return None, "Student NIM already exists."
        if student["email"].lower() == email:
            return None, "Student email already exists."

    return {"nim": nim, "nama": nama, "email": email}, None


def validate_course_payload(payload: dict, courses: list, exclude_id=None) -> tuple:
    """validate course entity fields and uniqueness of course code."""
    kode = str(payload.get("kode", "")).strip().upper()
    nama = str(payload.get("nama", "")).strip()
    raw_sks = payload.get("sks")

    if not kode or not nama or raw_sks is None or str(raw_sks).strip() == "":
        return None, "Course code, course name, and SKS are required."
    try:
        sks = int(raw_sks)
    except (TypeError, ValueError):
        return None, "SKS must be a valid integer."
    if sks < 1 or sks > 8:
        return None, "SKS must be between 1 and 8."

    for course in courses:
        if exclude_id is not None and course["id"] == exclude_id:
            continue
        if course["kode"].upper() == kode:
            return None, "Course code already exists."

    return {"kode": kode, "nama": nama, "sks": sks}, None


def validate_task_payload(payload: dict, students: list, courses: list) -> tuple:
    """validate task fields and verify student and course relations exist."""
    judul = str(payload.get("judul", "")).strip()
    deskripsi = str(payload.get("deskripsi", "")).strip()
    deadline = str(payload.get("deadline", "")).strip()
    prioritas = str(payload.get("prioritas", "")).strip()
    status = str(payload.get("status", "")).strip()

    if not judul or not deadline or not prioritas or not status:
        return None, "Title, deadline, priority, and status are required."
    if not is_valid_iso_date(deadline):
        return None, "Deadline must be a valid date (YYYY-MM-DD)."
    if prioritas not in VALID_PRIORITIES:
        return None, "Priority must be Low, Medium, or High."
    if status not in VALID_STATUSES:
        return None, "Status must be To Do, In Progress, or Completed."

    try:
        student_id = int(payload.get("student_id"))
        course_id = int(payload.get("course_id"))
    except (TypeError, ValueError):
        return None, "Valid student_id and course_id are required."

    if not any(s["id"] == student_id for s in students):
        return None, "Selected student does not exist."
    if not any(c["id"] == course_id for c in courses):
        return None, "Selected course does not exist."

    return {
        "judul": judul,
        "deskripsi": deskripsi,
        "deadline": deadline,
        "prioritas": prioritas,
        "status": status,
        "student_id": student_id,
        "course_id": course_id,
    }, None
