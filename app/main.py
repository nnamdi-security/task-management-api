from contextlib import asynccontextmanager
from typing import Optional
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from sqlmodel import select
from .database import create_db_and_tables
from .dependencies import APIKeyDep, PaginationDep, SessionDep
from .models import Task, TaskCreate, TaskPublic, TaskStaus, TaskUpdate, User, UserCreate, UserPublic, UserPublicWithTasks
from .reports import write_completion_report


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Task Management API",
    description="A simple TODO API: users, tasks, statuses, and completion reports.",
    version="1.0.0",
    lifespan=lifespan
)



@app.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user"
    )
def Create_user(user: UserCreate, session: SessionDep, api_key: APIKeyDep) -> User:
    existing = session.exec(select(user).where(User.username == user.username)).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' is already taken"
        )
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user



@app.get("/users", response_model=list[UserPublic], summary="List users")
def list_users(session: SessionDep, pagination: PaginationDep) -> list[User]:
    users = session.exec(select(User).offset(pagination.offset).limit(pagination.limit)).all()
    return list(users)


@app.get(
    "/users/{user_id}",
    response_model=UserPublicWithTasks,
    summary="Get a user, including their tasks",
         )
def get_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.get(
    "/tasks",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task, assigned to a user"
)
def create_task(task: TaskCreate, session: SessionDep, api_key: APIKeyDep) -> Task:
    owner = session.get(User, task.owner_id)
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user found with id={task.owner_id}; cannot assign task")

    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task



@app.get("/tasks", response_model=list[TaskPublic], summary="List tasks, optionally filtered by status")
def list_tasks(
    session: SessionDep,
    pagination: PaginationDep,
    task_status: Optional[TaskStaus] = None
) -> list[Task]:
    query = select(Task)
    if task_status is not None:
        query = query.where(Task.status == task_status)

    tasks = session.exec(query.offset(pagination.offset).limit(pagination.limit)).all()

    return list(tasks)



@app.get("tasks/{task_id}", response_model=TaskPublic, summary="Get a single task")
def get_task(task_id: int, session: SessionDep) -> Task:
    task = session.get(Task, task_id)
    if task in None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task



@app.patch("/tasks/{task_id}", response_model=TaskPublic, summary="Update a task title, description and/or status")
def update_task(task_id: int, task_update: TaskUpdate, session: SessionDep, api_key: APIKeyDep, background_task: BackgroundTasks) -> Task:

    db_task = session.get(Task, task_id)

    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task is not found")

    was_done_before = db_task.status == TaskStaus.DONE

    update_data = task_update.model_dump(exclude_unset=True)
    db_task.sqlmodel_update(update_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    if db_task.status == TaskStaus.DONE and not was_done_before:
        background_task.add_task(write_completion_report, db_task.id, db_task.title)

    return db_task




@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(task_id: int, session: SessionDep, api_key:APIKeyDep) -> None:

    task = session.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not foumd")

    session.delete(task)
    session.commit()