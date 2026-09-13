# FastAPI Assignments

A collection of FastAPI projects built for the fullstack/AI training
programme — each folder is a standalone assignment with its own
`main.py` (or `app/` package), tests, and dependencies.

## Projects

| Folder | Assignment | Demonstrates |
|---|---|---|
| `Payment-Processing-API/` | Payment Processing API | Request body validation, custom `field_validator`s (Luhn check, expiry date logic), simulated auth/decline flow |
| `Vehicle-Inventory-API/` | Vehicle Inventory API | Path parameters (`Path`), query parameters (`Query`), `Annotated`-style validation, filtering/search |
| `Flight-Booking-API/` | Flight Booking API | Nested request-body models, `Enum` for fixed choices (seat preference), `EmailStr`, cross-field validation |
| `VIP-Registration-Desk/` | Code quiz — VIP Registration Desk | Header & cookie *parameter models*, `response_model` filtering (Extra Models pattern), status codes, pre-filled `/docs` examples |
| `task-management-api/` | Task Management API | SQLModel + SQLite, foreign-key relationships, dependency injection (session, API key, pagination), background tasks |

Each folder has its own `README.md` (where present) or docstring header
in `main.py` explaining its specific endpoints and the doc chapters it's
built from.

## Common stack

- **FastAPI** + **Pydantic v2** for request/response validation
- **SQLModel** (task-management-api only) for the database layer
- **pytest** + **httpx** (`TestClient`) for tests
- **uv** for dependency and environment management, one `.venv` per project

## Running any project

From inside a project's folder:

```bash
uv add --dev pytest httpx   # plus whatever that project's deps are
uv run fastapi dev          # or: uv run fastapi dev app/main.py
uv run pytest -v
```

Each project's interactive docs are at `http://127.0.0.1:8000/docs` once
running.

## Why these patterns

Every project cites the specific FastAPI/Pydantic documentation chapter
its validation or design choice comes from, right in the code comments —
the goal throughout has been to learn the *why* behind each pattern
(response models, dependency injection, parameter models, background
tasks), not just produce working endpoints.
