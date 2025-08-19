from datetime import datetime

import jwt
from sqlalchemy import Integer, func, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from auth.app.security import security
from auth.app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    fullname: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
