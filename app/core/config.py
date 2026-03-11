from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Database settings

DATABASE_URL = getenv('DATABASE_URL')

# JWT settings

SECRET_KEY = getenv('SECRET_KEY', 'change-me-in-production')
ALGORITHM = getenv('ALGORITHM', 'HS256') 
TOKEN_EXPIRE_MINUTES = int(getenv('TOKEN_EXPIRE_MINUTES', '30'))