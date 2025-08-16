import jwt
import uuid
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from pydantic import BaseModel
from starlette import status

SECRET_KEY = "SECRET_KEY"
ALGORITHM = "HS256"

security_scheme = HTTPBearer()


class TokenData(BaseModel):
    sub: str | None = None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(sub=user_id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_author_id(
        token_data: TokenData = Depends(get_current_user)
) -> uuid.UUID:
    return uuid.UUID(token_data.sub)
