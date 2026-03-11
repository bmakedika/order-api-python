from app.core.security import hash_password
from app.core.config import ADMIN_PASSWORD, USER_PASSWORD

FAKE_USERS = {
    'admin': { 
        'username': 'admin',
        'hashed_password': hash_password(ADMIN_PASSWORD),
        'role': 'admin' 
    },
    'user': {
        'username': 'user',
        'hashed_password': hash_password(USER_PASSWORD),
        'role': 'user'
    }
}