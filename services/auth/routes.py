from typing import List

from fastapi import HTTPException, Depends, Response
from fastapi import APIRouter
from . import schemas
from .security import get_current_user, get_users, users_db, security, config

router = APIRouter(
    prefix='/auth',
    tags=['Аутентификация']
)


@router.get("/users", response_model=List[schemas.UserPublic])
def get_users(data_users=Depends(get_users)):
    return data_users


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/register")
async def register_user(user: schemas.UserRegister, data_users=Depends(get_users)):
    for us in data_users:
        if user.username == us.username or user.id == us.id:
            raise HTTPException(status_code=400, detail="Пользователь с таким username или id уже есть")

    new_user = schemas.UserInDB(**user.model_dump())

    users_db.append(new_user)
    return {'status': True, 'your_id': new_user.id}


@router.post("/login")
async def login(credentials: schemas.UserLogin, response: Response, data_users=Depends(get_users)):
    for user in data_users:
        if user.username == credentials.username and user.password == credentials.password:
            token = security.create_access_token(uid=str(user.id))
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
            return {"status": 'success', "access_token": token}
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "Вы успешно вышли из системы"}


@router.get("/protected", dependencies=[Depends(security.access_token_required)])
def protected():
    return {"access": True}
