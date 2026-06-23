import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)
)

PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", 15)
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

CACHE_EXPIRE_SECONDS = int(
    os.getenv("CACHE_EXPIRE_SECONDS", 300)
)

LOGIN_RATE_LIMIT = int(
    os.getenv("LOGIN_RATE_LIMIT", 5)
)

REGISTER_RATE_LIMIT = int(
    os.getenv("REGISTER_RATE_LIMIT", 3)
)

FORGOT_PASSWORD_RATE_LIMIT = int(
    os.getenv("FORGOT_PASSWORD_RATE_LIMIT", 3)
)

RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv("RATE_LIMIT_WINDOW_SECONDS", 60)
)