from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Header, HTTPException
from app.core.config import SECRET_KEY, ALGORITHM, TOKEN_EXPIRE_MINUTES


def create_access_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': username,
        'role': role,
        'exp': expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid or expired token')


def require_admin(authorization: str = Header()):
    if not authorization.startswith('Bearer'):
        raise HTTPException(status_code=401, detail='Missing token')
    token = authorization.removeprefix('Bearer')
    payload = decode_token(token)
    if payload.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')


def require_user(authorization: str = Header()):
    if not authorization.startswith('Bearer'):
        raise HTTPException(status_code=401, detail='Missing token')
    token = authorization.removeprefix('Bearer')
    return decode_token(token)











