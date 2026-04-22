from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.repos.user_repo import create, get_by_email


# Initialize password context

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# register user

def register_user(db: Session, username: str, email: str, password: str):
    # Check if user already exists
    existing_user = get_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=409, detail='Conflict')
    
    # Hash the password
    hashed_password = pwd_context.hash(password)
    return create(db, {
        'username': username,
        'email': email,
        'hashed_password': hashed_password
    })

# login user

def login_user(db: Session, email: str, password: str):
    user = get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    return user