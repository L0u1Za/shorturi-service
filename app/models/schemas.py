from pydantic import BaseModel, HttpUrl
from typing import Optional
import datetime

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None

class UpdateLinkRequest(BaseModel):
    new_url: HttpUrl

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(UserCreate):
    id: int
    hashed_password: str
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
