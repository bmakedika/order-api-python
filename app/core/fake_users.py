from app.core.security import hash_password

FAKE_USERS = {
    'admin': { 
        'username': 'admin',
        'hashed_password': hash_password('admin-secret'),
        'role': 'admin' 
    },
    'user': {
        'username': 'user',
        'hashed_password': hash_password('user-secret'),
        'role': 'user'
    }
}