from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session_maker
from .repository import UsersRepository
from .service import UserService, TokenService

bearer_scheme = HTTPBearer()


async def get_async_session() -> AsyncSession:
    """Создаёт и управляет сессией БД для одного запроса"""
    async with async_session_maker() as session:
        yield session


async def get_user_repo(
        session: AsyncSession = Depends(get_async_session)
) -> UsersRepository:
    """Создаёт репозиторий с сессией БД"""
    return UsersRepository(session)


def get_token_service() -> TokenService:
    """Создаёт сервис с созданием/проверкой токена JWT"""
    return TokenService()


def get_user_service_without_token(
        repo: UsersRepository = Depends(get_user_repo)
) -> UserService:
    return UserService(repo)


async def get_user_service(
        repo: UsersRepository = Depends(get_user_repo),
        token_service: TokenService = Depends(get_token_service)
) -> UserService:
    """Создаёт сервис с репозиторием"""
    return UserService(repo, token_service)


def get_current_user_payload(
        token_service: TokenService = Depends(),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    """
    Зависимость, которая проверяет Bearer токен и возвращает его payload.
    """
    return token_service.verify_token(credentials.credentials)
