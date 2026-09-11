from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import User, UserUpdate
from app.db import users_database, get_user_by_username
from app.dependencies import (get_current_user, hash_password)


router = APIRouter()


@router.post("/user", response_model=User, summary="Create user")
def create_user(user: User):
    if get_user_by_username(user.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    new_user = user.model_dump()
    new_user["id"] = len(users_database) + 1
    new_user["password"] = hash_password(user.password)
    new_user["group"] = "user"  # Default group
    users_database.append(new_user)
    return new_user


@router.get("/user/{user_id}", response_model=User, summary="Get user")
def get_user(user_id: int):
    for el in users_database:
        if el["id"] == user_id:
            return el
    raise HTTPException(status_code=404, detail="User not found")


@router.patch("/user/{user_id}", response_model=User, summary="Update user")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    if current_user["group"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    for idx, el in enumerate(users_database):
        if el["id"] == user_id:
            updated_user = el.copy()
            updated_user["name"] = user_update.name
            users_database[idx] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/user/{user_id}", summary="Delete user")
def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    if current_user["group"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    for idx, el in enumerate(users_database):
        if el["id"] == user_id:
            del users_database[idx]
            return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
