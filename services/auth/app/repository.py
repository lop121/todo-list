from services.auth.app.models import User
from services.utils.repository import SQLRepository


class UsersRepository(SQLRepository):
    model = User
