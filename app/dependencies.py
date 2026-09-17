import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from sqlalchemy import func, select
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.db import get_session, User, Ad

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 48

security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_token(username: str, group: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": username,
        "group": group,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        group: str = payload.get("group")
        if username is None or group is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception

    return {
        "id": user["id"],
        "name": user["name"],
        "group": user["group"],
    }


def require_admin(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if current_user["group"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_user(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return current_user

async def create_user(name: str, password: str, group: str = "user") -> dict:
    async with get_session() as session:
        user = User(name=name, password=password, group=group)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user.to_dict()


async def get_user_by_username(username: str) -> Optional[dict]:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.name == username))
        user = result.scalar_one_or_none()
        return user.to_dict() if user else None


async def get_user_by_id(user_id: int) -> Optional[dict]:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user.to_dict() if user else None


async def get_all_users() -> list[dict]:
    async with get_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return [user.to_dict() for user in users]


async def update_user(user_id: int, updates: dict) -> Optional[dict]:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user.to_dict()


async def delete_user(user_id: int) -> bool:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        await session.delete(user)
        await session.commit()
        return True


async def create_ad(title: str, author: str, description: Optional[str] = None,
                    price: Optional[float] = None) -> dict:
    async with get_session() as session:
        ad = Ad(title=title, author=author, description=description, price=price)
        session.add(ad)
        await session.commit()
        await session.refresh(ad)
        return ad.to_dict()


async def get_ad(ad_id: int) -> Optional[dict]:
    async with get_session() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        return ad.to_dict() if ad else None


async def update_ad(ad_id: int, updates: dict) -> Optional[dict]:
    async with get_session() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        if not ad:
            return None
        for key, value in updates.items():
            if hasattr(ad, key):
                setattr(ad, key, value)
        await session.commit()
        await session.refresh(ad)
        return ad.to_dict()


async def delete_ad(ad_id: int) -> bool:
    async with get_session() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        if not ad:
            return False
        await session.delete(ad)
        await session.commit()
        return True


async def search_ads(
    id: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    author: Optional[str] = None,
    created_at: Optional[datetime] = None,
    page: int = 1,
    per_page: int = 10,
) -> dict:
    async with get_session() as session:
        query = select(Ad)
        count_query = select(func.count()).select_from(Ad)
        conditions = []
        if id is not None:
            conditions.append(Ad.id == id)
        if title is not None:
            conditions.append(Ad.title.ilike(f"%{title}%"))
        if description is not None:
            conditions.append(Ad.description.ilike(f"%{description}%"))
        if price is not None:
            conditions.append(Ad.price == price)
        if author is not None:
            conditions.append(Ad.author.ilike(f"%{author}%"))
        if created_at is not None:
            conditions.append(func.date(Ad.created_at) >= func.date(created_at))
        if conditions:
            query = query.where(*conditions)
            count_query = count_query.where(*conditions)
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        pages = (total + per_page - 1) // per_page if total > 0 else 0
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        result = await session.execute(query)
        ads = result.scalars().all()
        return {
            "items": [ad.to_dict() for ad in ads],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }