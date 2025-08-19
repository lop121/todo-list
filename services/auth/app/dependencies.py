from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth.app.database import async_session_maker
from services.auth.app.repository import UsersRepository
from services.auth.app.service import UserService


# def users_service():
#     return UserService(UsersRepository)

async def get_async_session() -> AsyncSession:
    """Создаёт и управляет сессией БД для одного запроса"""
    async with async_session_maker() as session:
        yield session


async def get_user_repo(
        session: AsyncSession = Depends(get_async_session)
) -> UsersRepository:
    """Создаёт репозиторий с сессией БД"""
    return UsersRepository(session)


async def get_user_service(
        repo: UsersRepository = Depends(get_user_repo)
) -> UserService:
    """Создаёт сервис с репозиторием"""
    return UserService(repo)
