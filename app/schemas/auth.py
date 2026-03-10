from pydantic import BaseModel as basemodel


class LoginRequest(basemodel):
    username: str
    password: str

class TokenResponse(basemodel):
    access_token: str
    token_type: str = 'bearer'