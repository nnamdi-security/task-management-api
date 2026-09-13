from collections.abc import Generator
from sqlmodel import Session, SQLModel, create_engine


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"



connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables() -> None:
    """Create every table registered on SQLModel.metadata (User, Task)."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Yields one session per request. FastAPI runs the code before the 'yield' on the way in, and the code after it (none needed here, since the 'with' block closes the session automatically)on the way out
    """
    with Session(engine) as session:
        yield session