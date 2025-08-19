from abc import ABC, abstractmethod

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def find_by_id(self, model_id: int):
        raise NotImplementedError

    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_by_username(self, username):
        pass

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class SQLRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, model_id: int):
        return await self.session.get(self.model, model_id)

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.scalar()

    async def find_by_username(self, username: str):
        """Ищет пользователя по имени пользователя."""
        query = select(self.model).where(self.model.username == username)

        result = await self.session.execute(query)
        user = result.scalars().first()

        return user

    async def find_all(self):
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()
