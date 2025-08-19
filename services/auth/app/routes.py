from typing import List
from fastapi import Depends, Response
from fastapi import APIRouter

from . import schemas
from .rabbit_client import RabbitClient
from .security import security
from .service import UserService
from .dependencies import get_user_service, get_user_service_without_token, get_current_user_payload, get_rabbit_client

router = APIRouter(
    prefix='/auth',
    tags=['Аутентификация']
)


@router.get("/users", response_model=List[schemas.UserPublic])
async def get_users(user_service: UserService = Depends(get_user_service)):
    return await user_service.get_users()


@router.post("/register")
async def register_user(
        user_in: schemas.UserRegister,
        user_service: UserService = Depends(get_user_service_without_token),
        notification_service: RabbitClient = Depends(get_rabbit_client)
):
    user_id = await user_service.add_user(user_in)
    notification_service.send_user_registered_notification(user_in.username)

    return {'your_id': user_id}


@router.post("/login")
async def login(
        credentials: schemas.UserLogin,
        response: Response,
        user_service: UserService = Depends(get_user_service)
):
    token_data = await user_service.login_user(credentials)

    response.set_cookie(
        key=security.config.JWT_ACCESS_COOKIE_NAME,
        value=token_data['access_token'],
        httponly=True
    )

    return token_data


@router.get("/protected", dependencies=[Depends(get_current_user_payload)])
def protected():
    """
    Этот эндпоинт доступен только для пользователей с валидным access_token.
    """
    return {"access": True}


@router.get("/me")
async def get_me(payload: dict = Depends(get_current_user_payload)):
    """
    Возвращает информацию о текущем пользователе из токена.
    """
    user_id = payload.get("sub")
    return {"user_id": user_id, "message": "Hello from your token!"}
