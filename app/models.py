from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class TaskStaus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"



class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    email: str = Field(max_length=50)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    tasks: list["Task"] = Relationship(back_populates="owner")


class UserCreate(UserBase):
    pass

class UserPublic(UserBase):
    id: int


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStaus = Field(default=TaskStaus.TODO)


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner_id: int = Field(foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    owner_id: int = Field(gt=0, description="ID of the user this task is assigned to")



class TaskUpdate(SQLModel):
    """Every field optional: a PATCH only needs  to send what's changing."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStaus] = None



class TaskPublic(TaskBase):
    id: int
    created_at: datetime
    owner_id: int



class UserPublicWithTasks(UserPublic):
    tasks: list[TaskPublic] = []