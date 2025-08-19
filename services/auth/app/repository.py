from auth.app.models import User
from utils.repository import SQLRepository


class UsersRepository(SQLRepository):
    model = User
