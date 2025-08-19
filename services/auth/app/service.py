from fastapi import HTTPException

from services.auth.app.schemas import UserInDB, UserRegister
from services.utils.repository import AbstractRepository


class UserService:
    def __init__(self, users_repo: AbstractRepository):
        self.users_repo = users_repo

    async def add_user(self, user: UserRegister):
        if await self.users_repo.find_by_username(user.username):
            raise HTTPException(400, "Username уже занят")
        new_user = UserInDB(**user.model_dump())
        user_id = await self.users_repo.add_one(new_user.model_dump())
        return user_id
