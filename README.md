# Student Task Manager

A web-based academic task management application built for the Cloud and Distributed Computing (*Komputasi Awan dan Terdistribusi*) course project.

## Technology Stack

- **Frontend:** HTML, custom CSS, vanilla JavaScript (Fetch API, ES Modules)
- **Backend:** Python Flask (REST API returning JSON over HTTP)
- **Storage:** In-memory Python lists and dictionaries (no persistent database; data resets when the server restarts)

## Project Structure

```text
StudentTaskManager/
├── backend/
│   ├── __init__.py
│   ├── app.py              # flask application factory and page/static routing
│   ├── auth.py             # register, login (email/nim), logout, password hashing, session guard
│   ├── data.py             # fictitious initial seed data and in-memory store
│   ├── validators.py       # server-side validation and deadline classification
│   └── routes/
│       ├── __init__.py
│       ├── dashboard.py    # live statistics, completion rate, upcoming deadlines
│       ├── tasks.py        # task crud, search, filter, sort, assignment
│       ├── courses.py      # course crud, search, sks filter, delete protection
│       └── students.py     # student crud, search, delete protection
├── frontend/
│   ├── css/
│   │   └── styles.css      # custom high-fidelity design system stylesheet
│   ├── js/
│   │   ├── api.js          # http fetch wrapper, token/cookie handling, formatters
│   │   ├── layout.js       # shared navbar, sidebar active state, sign out, alerts
│   │   ├── auth.js         # login and register handlers
│   │   ├── dashboard.js    # dashboard stats and upcoming deadlines renderer
│   │   ├── tasks.js        # task list, search/filter/sort, and crud form
│   │   ├── courses.js      # course list, search/filter, and crud form
│   │   └── students.js     # student list, search, and crud form
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── tasks.html
│   ├── courses.html
│   └── students.html
├── tests/
│   └── test_api.py         # end-to-end http api and restart-reset tests
├── requirements.txt
├── .gitignore
└── README.md
```

## Features

- **Authentication:** Register (with password hashing), Login via Email or NIM, Logout, in-memory session tokens (`HttpOnly` cookie + Bearer token support), and protected routes/APIs.
- **Dashboard:** Dynamic KPI counters (Total Tasks, To Do, In Progress, Completed, Overdue), Completion Rate progress bar, Upcoming Deadlines table, and entity summaries.
- **Tasks:** Full CRUD, search by title, filter by student, course, status, and priority, sort by deadline (nearest/latest), Task Assignment with backend relation checks, and Overdue / Due Today indicators.
- **Courses:** Full CRUD, search by code or name, filter by SKS, linked task count, and delete protection while linked to active tasks.
- **Students:** Full CRUD, search by NIM, name, or email, assigned task count, and delete protection while assigned to active tasks.

## How to Run

1. Open a terminal in the project root (`StudentTaskManager`).
2. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```powershell
   python backend/app.py
   ```
5. Open your browser at:
   `http://127.0.0.1:5000`

### Demo Login Account (Fictitious In-Memory Seed)

- **Email / NIM:** `demo@student.example.ac.id` or `220101000`
- **Password:** `password123`

*(You can also create a new account from the Register page; all accounts and records are stored in memory and reset when the server restarts.)*

## Running Automated HTTP Tests

```powershell
.\.venv\Scripts\python.exe tests/test_api.py
```
