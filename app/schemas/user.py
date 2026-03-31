from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


# create userRegister schema
class UserRegister(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: str
    role: str
    created_at: datetime