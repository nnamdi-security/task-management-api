# Task Management API

A simple Trello/Todoist-style API built with FastAPI + SQLModel: users,
tasks with a status workflow, and a simulated "completion report"
background task.

## Project structure

```
task-management-api/
├── app/
│   ├── __init__.py
│   ├── database.py      # SQLite engine + get_session dependency
│   ├── models.py         # User & Task (Base/table/Create/Public/Update variants)
│   ├── dependencies.py   # session, API key, and pagination dependencies
│   ├── reports.py        # background task: completion report logger
│   └── main.py           # FastAPI app + all routes
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── requirements.txt
└── README.md
```

## Architecture

![Architecture diagram](docs/architecture.png)

Client requests hit the FastAPI app, which resolves the session, API key,
and pagination dependencies, then reads/writes `User` and `Task` rows via
SQLModel against SQLite. Marking a task `done` also queues a background
task that appends a line to the completion log after the response is sent.

## Endpoints

| Method | Path | Requires API key | Notes |
|---|---|---|---|
| POST | `/users` | yes | 409 if username taken |
| GET | `/users` | no | paginated |
| GET | `/users/{user_id}` | no | includes the user's tasks |
| POST | `/tasks` | yes | 404 if `owner_id` doesn't exist |
| GET | `/tasks` | no | paginated, optional `task_status` filter |
| GET | `/tasks/{task_id}` | no | |
| PATCH | `/tasks/{task_id}` | yes | change title/description/status |
| DELETE | `/tasks/{task_id}` | yes | |

Task `status` is one of `todo`, `in_progress`, `done`. Marking a task
`done` (from any other status) queues a background task that appends a
line to `app/completion_reports.log` — it runs after the response is
already sent back to the client.

## Setup

```bash
uv add fastapi sqlmodel "uvicorn[standard]"
uv add --dev pytest httpx
uv run fastapi dev app/main.py
```

Interactive docs: http://127.0.0.1:8000/docs

All write operations (`POST`, `PATCH`, `DELETE`) require an `X-API-Key`
header. The demo key is `demo-secret-key` (override it by setting the
`TASK_API_KEY` environment variable) — e.g.:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "X-API-Key: demo-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"username": "amaka", "email": "amaka@example.com"}'
```

## Testing

```bash
uv run pytest tests/ -v
```

Tests run against an isolated in-memory SQLite database (via a
dependency override on `get_session`), so they never touch the real
`database.db` file.

## Reference

- [SQL (Relational) Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) — the overall User/Task/Base/Create/Public pattern
- [SQLModel — Relationships](https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/) — the foreign key + `Relationship()`
- [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) and [Classes as Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/) — `get_session`, `require_api_key`, `PaginationParams`
- [Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) — the completion report
- [Lifespan Events](https://fastapi.tiangolo.com/advanced/events/#lifespan) — table creation on startup
- [Testing](https://fastapi.tiangolo.com/tutorial/testing/) and [SQLModel — Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/) — the in-memory test database pattern
