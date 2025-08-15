from datetime import timedelta
from typing import List

import uuid
from fastapi import FastAPI, HTTPException, Depends, Response, status
from authx import AuthX, AuthXConfig, TokenPayload
from pydantic import BaseModel, Field

app = FastAPI(title='To-Do List')

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)

users = []


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


@app.get("/users", response_model=List[UserPublic], tags=['Дополнительно'])
def get_users():
    return users


def get_current_user(payload: TokenPayload = Depends(security.access_token_required), data_users=Depends(get_users)):
    user_id = payload.sub
    for user in data_users:
        if str(user.id) == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")


@app.get("/me", tags=['Дополнительно'])
def me(current_user=Depends(get_current_user)):
    return current_user


@app.post("/register", tags=['Основное'])
async def register_user(user: UserRegister, data_users=Depends(get_users)):
    for us in data_users:
        if user.username == us.username or user.id == us.id:
            raise HTTPException(status_code=400, detail="Пользователь с таким username или id уже есть")

    new_user = UserInDB(**user.dict())

    users.append(new_user)
    return {'status': True, 'your_id': new_user.id}


@app.post("/login", tags=['Основное'])
async def login(credentials: UserLogin, response: Response, data_users=Depends(get_users)):
    for user in data_users:
        if user.username == credentials.username and user.password == credentials.password:
            token = security.create_access_token(uid=str(user.id))
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
            return {"status": 'success', "access_token": token}
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@app.post("/logout", tags=['Основное'])
def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "Вы успешно вышли из системы"}


@app.get("/protected", dependencies=[Depends(security.access_token_required)], tags=['Дополнительно'])
def protected():
    return {"access": True}
