from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

DATABASE_URL = "sqlite+aiosqlite:///./auth/auth.sqlite"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
