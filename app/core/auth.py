from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import uuid
from app.core.config import (
    ACCESS_SECRET_KEY,
    REFRESH_SECRET_KEY,
    ALGORITHM,
    TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_ISSUER,
    JWT_AUDIENCE,
)
from app.core.token_blacklist import is_jti_blacklisted

security = HTTPBearer()


def create_access_token(subject: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'sub': subject,
        'role': role,
        'type': 'access',
        'iss': JWT_ISSUER,
        'aud': JWT_AUDIENCE,
        'iat': int(now.timestamp()),
        'jti': str(uuid.uuid4()),
        'exp': now + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'sub': subject,
        'role': role,
        'type': 'refresh',
        'iss': JWT_ISSUER,
        'aud': JWT_AUDIENCE,
        'iat': int(now.timestamp()),
        'jti': str(uuid.uuid4()),
        'exp': now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        unverified = jwt.get_unverified_claims(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail='Invalid or expired token',
        )

    token_type = unverified.get('type')
    if token_type == 'refresh':
        key = REFRESH_SECRET_KEY
    else:
        key = ACCESS_SECRET_KEY

    try:
        return jwt.decode(
            token,
            key,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail='Invalid or expired token',
        )


def require_role(required_role: str = None):
    def role_verifier(credentials=Depends(security)):
        payload = decode_token(credentials.credentials)

        if payload.get('type') != 'access':
            raise HTTPException(
                status_code=401,
                detail='Invalid token type',
            )

        jti = payload.get('jti')
        if jti and is_jti_blacklisted(jti):
            raise HTTPException(
                status_code=401,
                detail='Token has been revoked',
            )

        if required_role:
            user_role = payload.get('role')
            if user_role != required_role:
                raise HTTPException(
                    status_code=403,
                    detail='Forbidden',
                )
        return payload
    return role_verifier


# Backward-compatible aliases
require_user = require_role()
require_admin = require_role('admin')