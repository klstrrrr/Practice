# TaskFlow backend

TaskFlow is a beginner-friendly Flask REST API backed by SQLite. This project
contains only the database and backend; it does not include a frontend.

## Project files

- `backend/database.py` opens and closes SQLite connections and creates the
  `users` and `tasks` tables, including the task-status constraint.
- `backend/models/user.py` contains database operations for user records.
- `backend/models/task.py` contains database operations for tasks, always
  scoped to their owning user.
- `backend/routes/auth.py` implements registration, login, and logout. Passwords
  are stored as Werkzeug password hashes, never as plain text.
- `backend/routes/tasks.py` implements authenticated task CRUD and validates
  task fields and statuses.
- `backend/app.py` configures Flask, initializes `database/taskflow.db`, and
  registers the API routes.
- `requirements.txt` lists the Python package dependency.
- `.gitignore` excludes the local SQLite database and Python-generated files.

## Run locally

From the project folder, create and activate a virtual environment, install the
dependency, and start the server:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m backend.app
```

The database is created automatically at `database/taskflow.db` when the app
starts. Set `TASKFLOW_SECRET_KEY` to a private random value before deployment;
the built-in key is only for local development.

## API

All request and response bodies use JSON. Register with
`POST /api/register` and `{"username":"sam","password":"example"}`. Then log in
with `POST /api/login` using the same fields. Flask stores the login in a
session cookie; clients must retain and send that cookie when calling task
routes. `POST /api/logout` clears the session.

- `GET /api/tasks` — list the signed-in user's tasks.
- `GET /api/tasks/<id>` — get one of that user's tasks.
- `POST /api/tasks` — create a task; `title` is required, `description` is
  optional, and `status` defaults to `To Do`.
- `PUT /api/tasks/<id>` — update one or more of `title`, `description`, and
  `status`.
- `DELETE /api/tasks/<id>` — delete one of that user's tasks.

Allowed statuses are `To Do`, `In Progress`, and `Done`. Task routes return
`401` when the client is not logged in, `404` when the task does not exist for
that user, and `400` for invalid input. A duplicate username returns `409`.
