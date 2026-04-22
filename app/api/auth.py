from fastapi import APIRouter, Depends, HTTPException, Request, Response, Header
import time
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import create_access_token, create_refresh_token, decode_token
from app.core.refresh_store import store_refresh_token, get_subject_for_refresh_token, revoke_refresh_token
from app.schemas.auth import AccessTokenResponse, RefreshRequest, LogoutRequest
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.services import user_service
from app.repos.user_repo import get_by_email
from app.core.config import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    AUTH_COOKIE_SECURE,
    AUTH_COOKIE_SAMESITE,
)
from app.core.token_blacklist import blacklist_jti


router = APIRouter()

REFRESH_COOKIE_NAME = 'refresh_token'

def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite=AUTH_COOKIE_SAMESITE,
        path='/auth',
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path='/auth')


@router.post('/auth/register', response_model=UserResponse)
def register(body: UserRegister, db: Session = Depends(get_db)):
    return user_service.register_user(db, username=body.username, email=body.email, password=body.password)


@router.post('/auth/login', response_model=AccessTokenResponse)
def login(body: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = user_service.login_user(db, email=body.email, password=body.password)

    access_token = create_access_token(subject=user.email, role=user.role)
    refresh_token = create_refresh_token(subject=user.email, role=user.role)
    store_refresh_token(refresh_token, subject=user.email)
    set_refresh_cookie(response, refresh_token)
    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


@router.post('/auth/refresh', response_model=AccessTokenResponse)
def refresh(
    request: Request, 
    response: Response,
    body: RefreshRequest | None = None,
    db: Session = Depends(get_db),
    ):
    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    body_token = body.refresh_token if body else None
    refresh_token = body_token or cookie_token

    if not refresh_token:
        raise HTTPException(status_code=401, detail='Missing refresh token')
    
    payload = decode_token(refresh_token)
    if payload.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    
    
    subject = get_subject_for_refresh_token(refresh_token)
    if not subject:
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    
    
    user = get_by_email(db, email=subject)
    if not user:
        revoke_refresh_token(refresh_token)
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    
    revoke_refresh_token(refresh_token)
    new_access = create_access_token(subject=user.email, role=user.role)
    new_refresh = create_refresh_token(subject=user.email, role=user.role)
    store_refresh_token(new_refresh, subject=user.email)
    set_refresh_cookie(response, new_refresh)
    return {
        'access_token': new_access,
        'token_type': 'bearer'
    }

@router.post('/auth/logout')
def logout(
    request: Request,
    response: Response,
    authorization: str | None = Header(default=None),
    body: LogoutRequest | None = None
    ):
    
    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    body_token = body.refresh_token if body else None
    refresh_token = body_token or cookie_token

    if refresh_token:
        revoke_refresh_token(refresh_token)
    
    clear_refresh_cookie(response)

   
    if authorization and authorization.startswith('Bearer '):
        access_token = authorization.removeprefix('Bearer ').strip()
        payload = decode_token(access_token)

        if payload.get('type') == 'access':
            jti = payload.get('jti')
            exp = payload.get('exp')
            if jti and exp:
                ttl = int(exp - time.time())
                if ttl > 0:
                    blacklist_jti(jti, ttl_seconds=ttl)

    return {'detail': 'Logged out successfully'}