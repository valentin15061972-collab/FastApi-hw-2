from pydantic import BaseModel
from datetime import datetime


class Ad(BaseModel):
    title: str
    description: str | None = None
    price: float | None = None
    author: str
    created_at: datetime | None = None


class AdCreate(BaseModel):
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
    name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int
