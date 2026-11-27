"""end-to-end http api and in-memory restart tests for student task manager."""

import http.cookiejar
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
PYTHON_EXE = sys.executable
BASE_URL = "http://127.0.0.1:5055"


class HttpClient:
    """simple urllib wrapper preserving cookies across requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            _NoRedirectHandler(),
        )

    def request(self, method: str, path: str, body=None, headers=None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req_headers = {"Content-Type": "application/json", **(headers or {})}
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=req_headers,
            method=method,
        )
        try:
            with self.opener.open(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, _parse_json(raw), dict(resp.headers)
        except urllib.error.HTTPError as err:
            raw = err.read().decode("utf-8")
            return err.code, _parse_json(raw), dict(err.headers)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """prevent automatic redirects so 302 protection checks can be asserted."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _parse_json(raw: str):
    """parse json text safely or return raw string."""
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def start_server(port: int) -> subprocess.Popen:
    """launch flask server on a dedicated test port and wait until ready."""
    code = (
        "import sys; sys.path.insert(0, r'" + PROJECT_ROOT + "'); "
        "from backend.app import app; "
        f"app.run(host='127.0.0.1', port={port}, debug=False)"
    )
    proc = subprocess.Popen(
        [PYTHON_EXE, "-c", code],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/login.html", timeout=1)
            return proc
        except Exception:
            time.sleep(0.2)
    proc.terminate()
    raise RuntimeError("flask test server failed to start in time")


def run_tests():
    """execute full http test suite and verify state reset after restart."""
    server = start_server(5055)
    try:
        client = HttpClient(BASE_URL)

        # 1. verify unauthenticated protection on pages and apis
        status, _, headers = client.request("GET", "/dashboard.html")
        assert status == 302 and "/login.html" in headers.get("Location", ""), f"expected redirect, got {status}"

        status, body, _ = client.request("GET", "/api/dashboard")
        assert status == 401, f"expected 401 on protected api, got {status}"

        # 2. verify registration validation and success
        status, body, _ = client.request("POST", "/api/auth/register", {
            "full_name": "Test User",
            "nim": "220109999",
            "email": "test.user@student.example.ac.id",
            "password": "secret123",
            "confirm_password": "mismatch",
        })
        assert status == 400 and "match" in body["error"].lower()

        status, body, _ = client.request("POST", "/api/auth/register", {
            "full_name": "Test User",
            "nim": "220109999",
            "email": "test.user@student.example.ac.id",
            "password": "secret123",
            "confirm_password": "secret123",
        })
        assert status == 201, f"register failed: {body}"

        # 3. verify invalid credentials and login via email and nim
        status, body, _ = client.request("POST", "/api/auth/login", {
            "identifier": "test.user@student.example.ac.id",
            "password": "wrongpassword",
        })
        assert status == 401

        status, body, _ = client.request("POST", "/api/auth/login", {
            "identifier": "220109999",
            "password": "secret123",
        })
        assert status == 200 and body["user"]["email"] == "test.user@student.example.ac.id"

        # verify password hashing was used in store via backend module check
        from backend.data import create_initial_data
        seed = create_initial_data()
        assert len(seed["accounts"]) == 4
        assert all(acc["password_hash"] != "assalam5g" for acc in seed["accounts"])

        # 4. verify dashboard stats match initial seed data
        status, dash, _ = client.request("GET", "/api/dashboard")
        assert status == 200
        assert dash["stats"]["total_tasks"] == 8
        assert dash["stats"]["completed"] == 2
        assert dash["stats"]["overdue"] == 1
        assert dash["stats"]["due_today"] == 1
        assert dash["stats"]["completion_rate"] == 25

        # 5. verify student crud and delete protection
        status, body, _ = client.request("GET", "/api/students?search=Nadia")
        assert status == 200 and len(body["students"]) == 1

        status, body, _ = client.request("DELETE", "/api/students/1")
        assert status == 409, f"expected 409 for student with tasks, got {status}"

        status, body, _ = client.request("POST", "/api/students", {
            "nim": "220109888",
            "nama": "Sinta Dewi",
            "email": "sinta.dewi@student.example.ac.id",
        })
        assert status == 201
        new_student_id = body["student"]["id"]

        status, body, _ = client.request("PUT", f"/api/students/{new_student_id}", {
            "nim": "220109888",
            "nama": "Sinta Dewi Updated",
            "email": "sinta.dewi@student.example.ac.id",
        })
        assert status == 200 and body["student"]["nama"] == "Sinta Dewi Updated"

        # 6. verify course crud, filtering, and delete protection
        status, body, _ = client.request("GET", "/api/courses?sks=2")
        assert status == 200 and len(body["courses"]) == 1

        status, body, _ = client.request("DELETE", "/api/courses/1")
        assert status == 409

        status, body, _ = client.request("POST", "/api/courses", {
            "kode": "if404",
            "nama": "Distributed Systems",
            "sks": 4,
        })
        assert status == 201 and body["course"]["kode"] == "IF404"
        new_course_id = body["course"]["id"]

        status, body, _ = client.request("PUT", f"/api/courses/{new_course_id}", {
            "kode": "IF404",
            "nama": "Distributed Cloud Systems",
            "sks": 4,
        })
        assert status == 200 and body["course"]["nama"] == "Distributed Cloud Systems"

        # 7. verify task crud, relation validation, and search/filter/sort
        status, body, _ = client.request("POST", "/api/tasks", {
            "judul": "Invalid Relation Task",
            "deskripsi": "Should fail",
            "deadline": date.today().isoformat(),
            "prioritas": "High",
            "status": "To Do",
            "student_id": 9999,
            "course_id": new_course_id,
        })
        assert status == 400

        status, body, _ = client.request("POST", "/api/tasks", {
            "judul": "Consensus Algorithm Summary",
            "deskripsi": "Compare Raft and Paxos.",
            "deadline": date.today().isoformat(),
            "prioritas": "High",
            "status": "In Progress",
            "student_id": new_student_id,
            "course_id": new_course_id,
        })
        assert status == 201 and body["task"]["deadline_status"] == "due_today"
        new_task_id = body["task"]["id"]

        # confirm newly linked student & course cannot be deleted while task exists
        status, _, _ = client.request("DELETE", f"/api/students/{new_student_id}")
        assert status == 409
        status, _, _ = client.request("DELETE", f"/api/courses/{new_course_id}")
        assert status == 409

        # test search, filter, and sort
        status, body, _ = client.request("GET", f"/api/tasks?search=Consensus&student_id={new_student_id}&priority=High&sort=desc")
        assert status == 200 and len(body["tasks"]) == 1

        # update task to completed and confirm dashboard stats update dynamically
        status, body, _ = client.request("PUT", f"/api/tasks/{new_task_id}", {
            "judul": "Consensus Algorithm Summary",
            "deskripsi": "Updated notes",
            "deadline": date.today().isoformat(),
            "prioritas": "Medium",
            "status": "Completed",
            "student_id": new_student_id,
            "course_id": new_course_id,
        })
        assert status == 200 and body["task"]["status"] == "Completed"

        status, dash2, _ = client.request("GET", "/api/dashboard")
        assert dash2["stats"]["total_tasks"] == 9
        assert dash2["stats"]["completed"] == 3
        assert dash2["stats"]["completion_rate"] == 33

        # delete task, then unlinked student and course can be deleted
        status, _, _ = client.request("DELETE", f"/api/tasks/{new_task_id}")
        assert status == 200
        status, _, _ = client.request("DELETE", f"/api/students/{new_student_id}")
        assert status == 200
        status, _, _ = client.request("DELETE", f"/api/courses/{new_course_id}")
        assert status == 200

        # 8. verify logout invalidates session
        status, _, _ = client.request("POST", "/api/auth/logout")
        assert status == 200
        status, _, _ = client.request("GET", "/api/dashboard")
        assert status == 401
    finally:
        server.terminate()
        server.wait(timeout=5)

    # 9. restart server and verify in-memory state resets cleanly
    server2 = start_server(5055)
    try:
        client2 = HttpClient(BASE_URL)
        # registered user from previous run must not persist after restart
        status, _, _ = client2.request("POST", "/api/auth/login", {
            "identifier": "test.user@student.example.ac.id",
            "password": "secret123",
        })
        assert status == 401, "expected registered user to disappear after restart"

        # seeded group accounts still work and counts reset to initial 8 tasks
        status, body, _ = client2.request("POST", "/api/auth/login", {
            "identifier": "hisyamnurdiatmoko@student.telkomuniversity.ac.id",
            "password": "assalam5g",
        })
        assert status == 200 and body["user"]["full_name"] == "Hisyam Nurdiatmoko"

        # verify another group member can sign in via nim
        status, body2, _ = client2.request("POST", "/api/auth/login", {
            "identifier": "103112400024",
            "password": "assalam5g",
        })
        assert status == 200 and body2["user"]["full_name"] == "Setyo Nugroho"

        status, dash, _ = client2.request("GET", "/api/dashboard")
        assert status == 200 and dash["stats"]["total_tasks"] == 8
    finally:
        server2.terminate()
        server2.wait(timeout=5)

    print("ALL HTTP API AND IN-MEMORY RESTART TESTS PASSED.")


if __name__ == "__main__":
    run_tests()
