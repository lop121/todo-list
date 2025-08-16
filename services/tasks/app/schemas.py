import uuid
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskInDB(TaskCreate):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    author_id: uuid.UUID


class Task(TaskInDB):
    pass


class TaskWithAuthorUsername(Task):
    author_username: str
