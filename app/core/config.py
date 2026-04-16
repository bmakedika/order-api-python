from os import getenv
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# Database settings

DATABASE_URL = getenv('DATABASE_URL')

# JWT settings (NEW)

ACCESS_SECRET_KEY = getenv('ACCESS_SECRET_KEY', getenv('SECRET_KEY', 'change-me-in-production'))
REFRESH_SECRET_KEY = getenv('REFRESH_SECRET_KEY', getenv('SECRET_KEY', 'change-me-in-production'))
ALGORITHM = getenv('ALGORITHM', 'HS256')
JWT_ISSUER = getenv('JWT_ISSUER', 'order-api')
JWT_AUDIENCE = getenv('JWT_AUDIENCE', 'order-api-client')

TOKEN_EXPIRE_MINUTES = int(getenv('TOKEN_EXPIRE_MINUTES', '30'))
REFRESH_TOKEN_EXPIRE_DAYS = int(getenv('REFRESH_TOKEN_EXPIRE_DAYS', '30'))

# Backward-comptablitiy (optional): keep old name if used elswhere

SECRET_KEY = getenv('SECRET_KEY', 'change-me-in-production')

# Admin and user credentials

ADMIN_PASSWORD = getenv('ADMIN_PASSWORD', 'admin-sercret')
USER_PASSWORD = getenv('USER_PASSWORD', 'user-sercret')

# Redis settings

REDIS_URL = getenv('REDIS_URL', 'redis://localhost:6379')