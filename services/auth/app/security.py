from datetime import timedelta

from authx import AuthX, AuthXConfig, TokenPayload
from fastapi import HTTPException, Depends, status

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_ALGORITHM = "HS256"

security = AuthX(config=config)

users_db = []


def get_users():
    return users_db


def get_current_user(payload: TokenPayload = Depends(security.access_token_required), data_users=Depends(get_users)):
    user_id = payload.sub
    for user in data_users:
        if str(user.id) == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
