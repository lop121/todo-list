from datetime import datetime

import jwt
from sqlalchemy import Integer, func, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from services.auth.app.database import Base
from services.auth.app.security import security


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    fullname: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())

    @property
    def token(self):
        now = datetime.utcnow()
        exp = (now + security.JWT_ACCESS_TOKEN_EXPIRES).timestamp()
        data = {
            "exp": exp,
            "email": self.id,
        }
        return jwt.encode(data, security.JWT_SECRET_KEY, algorithm=security.JWT_ALGORITHM)
