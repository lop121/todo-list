from datetime import datetime

from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str
    fullname: str | None = None


class UserInDB(UserRegister):
    created_at: datetime | None = datetime.now()


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    username: str
    full_name: str | None = None
