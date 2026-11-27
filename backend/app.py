"""flask application factory, api registration, and protected page serving."""

import os
import sys

from flask import Flask, redirect, request, send_from_directory

# ensure project root is on sys.path when invoked directly as python backend/app.py
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.auth import auth_bp, get_current_user
from backend.routes.courses import courses_bp
from backend.routes.dashboard import dashboard_bp
from backend.routes.students import students_bp
from backend.routes.tasks import tasks_bp

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
PROTECTED_PAGES = {"dashboard.html", "tasks.html", "courses.html", "students.html"}
AUTH_PAGES = {"login.html", "register.html"}


def create_app() -> Flask:
    """create and configure the flask application instance."""
    app = Flask(__name__, static_folder=None)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(students_bp)

    @app.before_request
    def handle_preflight():
        """respond immediately to cors preflight requests."""
        if request.method == "OPTIONS":
            return ("", 204)
        return None

    @app.after_request
    def add_cors_headers(response):
        """attach cors headers so frontend can also be hosted separately."""
        origin = request.headers.get("Origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    @app.get("/")
    def index():
        """redirect root requests based on authentication state."""
        if get_current_user():
            return redirect("/dashboard.html")
        return redirect("/login.html")

    @app.get("/<string:page_name>")
    def serve_page(page_name: str):
        """serve protected or auth html pages with server-side session checks."""
        if page_name in PROTECTED_PAGES:
            if not get_current_user():
                return redirect("/login.html")
            return send_from_directory(FRONTEND_DIR, page_name)

        if page_name in AUTH_PAGES:
            if get_current_user():
                return redirect("/dashboard.html")
            return send_from_directory(FRONTEND_DIR, page_name)

        return ("Not Found", 404)

    @app.get("/css/<path:filename>")
    def serve_css(filename: str):
        """serve custom stylesheets."""
        return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)

    @app.get("/js/<path:filename>")
    def serve_js(filename: str):
        """serve vanilla javascript modules."""
        return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
