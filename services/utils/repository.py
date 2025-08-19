from abc import ABC, abstractmethod

from sqlalchemy import insert
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
        return res

    async def find_by_username(self, username):
        return await self.session.get(self.model, username)
