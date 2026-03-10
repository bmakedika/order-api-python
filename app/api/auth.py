from fastapi import APIRouter, HTTPException
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.fake_users import FAKE_USERS
from app.core.security import verify_password
from app.core.auth import create_access_token

router = APIRouter()

@router.post('/auth/login', response_model=TokenResponse)
def login(body: LoginRequest):
    
    user = FAKE_USERS.get(body.username)
    if not user :
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    
    if not verify_password(body.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    
    token = create_access_token(
        username=user['username'],
        role=user['role']
    )

    return TokenResponse(access_token=token)