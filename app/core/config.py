from os import getenv
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# Database settings

DATABASE_URL = getenv('DATABASE_URL')

# JWT settings

SECRET_KEY = getenv('SECRET_KEY', 'change-me-in-production')
ALGORITHM = getenv('ALGORITHM', 'HS256') 
TOKEN_EXPIRE_MINUTES = int(getenv('TOKEN_EXPIRE_MINUTES', '30'))
REFRESH_TOKEN_EXPIRE_DAYS = int(getenv('REFRESH_TOKEN_EXPIRE_DAYS', '30'))

# Admin and user credentials

ADMIN_PASSWORD = getenv('ADMIN_PASSWORD', 'admin-sercret')
USER_PASSWORD = getenv('USER_PASSWORD', 'user-sercret')

# Redis settings

REDIS_URL = getenv('REDIS_URL', 'redis://localhost:6379')