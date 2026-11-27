"""in-memory data store and fictitious seed records."""

from datetime import date, timedelta
from werkzeug.security import generate_password_hash


def _iso_offset(days: int) -> str:
    """return iso date string offset from today."""
    return (date.today() + timedelta(days=days)).isoformat()


def create_initial_data() -> dict:
    """build fresh initial in-memory lists and dictionaries."""
    return {
        # authentication accounts are separated from the student entity
        "accounts": [
            {
                "id": 1,
                "full_name": "Demo Student",
                "nim": "220101000",
                "email": "demo@student.example.ac.id",
                "password_hash": generate_password_hash("password123"),
            }
        ],
        # active user sessions mapped by session token
        "sessions": {},
        "students": [
            {
                "id": 1,
                "nim": "220101001",
                "nama": "Nadia Rahman",
                "email": "nadia.rahman@student.example.ac.id",
            },
            {
                "id": 2,
                "nim": "220101002",
                "nama": "Raka Wijaya",
                "email": "raka.wijaya@student.example.ac.id",
            },
            {
                "id": 3,
                "nim": "220101003",
                "nama": "Bima Pratama",
                "email": "bima.pratama@student.example.ac.id",
            },
            {
                "id": 4,
                "nim": "220101004",
                "nama": "Alya Putri",
                "email": "alya.putri@student.example.ac.id",
            },
            {
                "id": 5,
                "nim": "220101005",
                "nama": "Dimas Saputra",
                "email": "dimas.saputra@student.example.ac.id",
            },
        ],
        "courses": [
            {"id": 1, "kode": "IF301", "nama": "Cloud Computing", "sks": 3},
            {"id": 2, "kode": "IF302", "nama": "Web Programming", "sks": 3},
            {"id": 3, "kode": "IF201", "nama": "Database Systems", "sks": 3},
            {"id": 4, "kode": "IF202", "nama": "Computer Networks", "sks": 3},
            {"id": 5, "kode": "IF305", "nama": "System Security", "sks": 2},
        ],
        "tasks": [
            {
                "id": 1,
                "judul": "Inventory ER Diagram",
                "deskripsi": "Design entity-relationship diagram and normalize core tables.",
                "deadline": _iso_offset(-5),
                "prioritas": "Medium",
                "status": "Completed",
                "student_id": 1,
                "course_id": 3,
            },
            {
                "id": 2,
                "judul": "Packet Capture Analysis",
                "deskripsi": "Inspect TCP handshake and HTTP packets using Wireshark.",
                "deadline": _iso_offset(-3),
                "prioritas": "Low",
                "status": "Completed",
                "student_id": 2,
                "course_id": 4,
            },
            {
                "id": 3,
                "judul": "VPC Architecture Lab Report",
                "deskripsi": "Document public/private subnet routing and internet gateway setup.",
                "deadline": _iso_offset(-2),
                "prioritas": "High",
                "status": "To Do",
                "student_id": 1,
                "course_id": 1,
            },
            {
                "id": 4,
                "judul": "Web Interface Prototype",
                "deskripsi": "Build responsive HTML/CSS prototype screens for task tracking.",
                "deadline": _iso_offset(0),
                "prioritas": "Medium",
                "status": "In Progress",
                "student_id": 3,
                "course_id": 2,
            },
            {
                "id": 5,
                "judul": "Cloud Application Design",
                "deskripsi": "Prepare REST API contract and three-tier deployment plan.",
                "deadline": _iso_offset(2),
                "prioritas": "High",
                "status": "In Progress",
                "student_id": 4,
                "course_id": 1,
            },
            {
                "id": 6,
                "judul": "Academic Schema Normalization",
                "deskripsi": "Convert unnormalized academic form records to 3NF relations.",
                "deadline": _iso_offset(5),
                "prioritas": "Medium",
                "status": "To Do",
                "student_id": 2,
                "course_id": 3,
            },
            {
                "id": 7,
                "judul": "Static Routing Configuration",
                "deskripsi": "Configure static routes across three simulated campus routers.",
                "deadline": _iso_offset(8),
                "prioritas": "Low",
                "status": "To Do",
                "student_id": 3,
                "course_id": 4,
            },
            {
                "id": 8,
                "judul": "REST Endpoint Integration",
                "deskripsi": "Connect client-side fetch actions with Flask JSON endpoints.",
                "deadline": _iso_offset(11),
                "prioritas": "High",
                "status": "To Do",
                "student_id": 1,
                "course_id": 2,
            },
        ],
    }


store = create_initial_data()


def next_id(items: list) -> int:
    """compute the next sequential integer id for a list of dicts."""
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def reset_store() -> None:
    """restore store contents to the initial seed state."""
    fresh = create_initial_data()
    for key, value in fresh.items():
        store[key] = value
