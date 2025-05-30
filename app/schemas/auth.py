from pydantic import BaseModel, EmailStr
from typing import Optional

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int

class TokenData(BaseModel):
    email: Optional[str] = None 