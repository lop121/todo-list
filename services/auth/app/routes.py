from datetime import datetime, timezone
from typing import List
import pika
from fastapi import HTTPException, Depends, Response
from fastapi import APIRouter
import json

from uuid import UUID

from . import schemas
from .security import get_current_user, get_users, security, config
from .service import UserService
from .dependencies import get_user_service

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
async def register_user(
        user_in: schemas.UserRegister,
        user_service: UserService = Depends(get_user_service)
):
    user_id = await user_service.add_user(user_in)

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        exchange_name = 'user_events'
        queue_name = 'notifications_queue'

        channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='user.registered')

        message_body = {
            "username": user_in.username,
            "time_create": datetime.now(timezone.utc).isoformat()
        }

        channel.basic_publish(
            exchange=exchange_name,
            routing_key='user.registered',
            body=json.dumps(message_body)
        )

        print(f" [x] Отправлено уведомление о пользователе: {user_in.username}")
        connection.close()
    except pika.exceptions.AMQPConnectionError:
        print(" [!] Ошибка с подключением к RabbitMQ, проверьте запущен ли сервер.")

    return {'your_id': user_id}


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


@router.get("/users/{user_id}", response_model=schemas.UserPublic)
async def get_user_info_by_id(user_id: UUID, data_users=Depends(get_users)):
    for user in data_users:
        if user.id == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")
