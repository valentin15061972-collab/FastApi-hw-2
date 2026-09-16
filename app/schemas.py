from pydantic import BaseModel
from datetime import datetime


class Advertisement(BaseModel):
    title: str
    description: str | None = None
    price: float | None = None
    author: str
    created_at: datetime | None = None


class AdvertisementCreate(BaseModel):
    title: str
    description: str | None = None
    price: float | None = None


class User(BaseModel):
    id: int | None = None
    name: str
    password: str
    group: str = "user"
    created_at: datetime | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    password: str | None = None
    group: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int
