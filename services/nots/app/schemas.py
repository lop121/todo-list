from datetime import datetime

from pydantic import BaseModel


class NotificationNewUser(BaseModel):
    username: str
    time_create: datetime
