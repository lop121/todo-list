from datetime import datetime, timezone
from typing import List
import pika
from fastapi import HTTPException, Depends, Response
from fastapi import APIRouter
import json

from uuid import UUID

from . import schemas
from .security import security, config
from .service import UserService
from .dependencies import get_user_service, get_user_service_without_token, get_current_user_payload

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
        user_service: UserService = Depends(get_user_service_without_token)
):
    user_id = await user_service.add_user(user_in)

    # try:
    #     connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    #     channel = connection.channel()
    #
    #     exchange_name = 'user_events'
    #     queue_name = 'notifications_queue'
    #
    #     channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
    #
    #     channel.queue_declare(queue=queue_name, durable=True)
    #     channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='user.registered')
    #
    #     message_body = {
    #         "username": user_in.username,
    #         "time_create": datetime.now(timezone.utc).isoformat()
    #     }
    #
    #     channel.basic_publish(
    #         exchange=exchange_name,
    #         routing_key='user.registered',
    #         body=json.dumps(message_body)
    #     )
    #
    #     print(f" [x] Отправлено уведомление о пользователе: {user_in.username}")
    #     connection.close()
    # except pika.exceptions.AMQPConnectionError:
    #     print(" [!] Ошибка с подключением к RabbitMQ, проверьте запущен ли сервер.")

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


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "Вы успешно вышли из системы"}


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
