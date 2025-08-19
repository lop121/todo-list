from datetime import timedelta

from authx import AuthX, AuthXConfig

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_ALGORITHM = "HS256"

security = AuthX(config=config)
