from pydantic import BaseModel as basemodel
from typing import Optional


class LoginRequest(basemodel):
    username: str
    password: str

# Cookie-only response (no refresh token in body)
class AccessTokenResponse(basemodel):
    access_token: str
    token_type: str = 'bearer'

# Legacy: keep if you still need it somewhere else
class TokenResponse(basemodel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

# In cookies-only response, refresh can comes from cookie, so body is optional
class RefreshRequest(basemodel):
    refresh_token: Optional[str] = None

class LogoutRequest(basemodel):
    refresh_token: Optional[str] = None