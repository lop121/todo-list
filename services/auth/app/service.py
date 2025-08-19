import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from auth.app.schemas import UserPublic
from utils.repository import AbstractRepository
from . import schemas, security
from .schemas import UserInDB, UserRegister

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenService:
    @staticmethod
    def create_access_token(user_id: int) -> str:
        token = security.security.create_access_token(uid=str(user_id))
        return token

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, security.config.JWT_SECRET_KEY, algorithms=[security.config.JWT_ALGORITHM])
            return payload
        except jwt.DecodeError as e:
            raise e


class UserService:
    def __init__(self, users_repo: AbstractRepository, token_service: TokenService | None = None):
        self.users_repo = users_repo
        self.token_service = token_service

    @staticmethod
    def hash_password(password: str) -> str:
        """Хэширует пароль и возвращает хэш в виде строки."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Сравнивает чистый пароль с хэшем."""
        return pwd_context.verify(plain_password, hashed_password)

    async def add_user(self, user: UserRegister):
        if await self.users_repo.find_by_username(user.username):
            raise HTTPException(400, "Username уже занят")

        user_data = user.model_dump()

        user_data["password"] = self.hash_password(user_data["password"])

        new_user = UserInDB(**user_data)
        user_id = await self.users_repo.add_one(new_user.model_dump())

        return user_id

    async def get_users(self):
        users = await self.users_repo.find_all()
        dto_users = [UserPublic.model_validate(row, from_attributes=True) for row in users]
        return dto_users

    async def authenticate_user(self, username: str, password: str):
        user = await self.users_repo.find_by_username(username)
        if not user or not self.verify_password(password, user.password):
            return None
        return user

    async def login_user(self, credentials: schemas.UserLogin) -> dict:
        """
        Обрабатывает логин: аутентифицирует и возвращает токен.
        """
        if not self.token_service:
            raise RuntimeError("TokenService не был предоставлен для UserService")

        user = await self.authenticate_user(credentials.username, credentials.password)

        if not user:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        access_token = self.token_service.create_access_token(user_id=user.id)

        return {"access_token": access_token}

    # @staticmethod
    # def create_access_token(user_id: int) -> str:
    #     now = datetime.utcnow()
    #     exp = (now + security.JWT_ACCESS_TOKEN_EXPIRES).timestamp()
    #     data = {
    #         "exp": exp,
    #         "id": user_id,
    #     }
    #     return jwt.encode(data, security.JWT_SECRET_KEY, algorithm=security.JWT_ALGORITHM)
