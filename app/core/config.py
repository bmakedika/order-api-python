from os import getenv

SECRET_KEY = getenv('SECRET_KEY', 'change-me-in-production')
ALGORITHM = getenv('ALGORITHM', 'HS256') 
TOKEN_EXPIRE_MINUTES = int(getenv('TOKEN_EXPIRE_MINUTES', '30'))