from pydantic import BaseModel, Field
import uuid


class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str | None = None


class UserInDB(UserRegister):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    username: str
    full_name: str | None = None
