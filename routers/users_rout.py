from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import User, UserUpdate
from app.dependencies import get_user_by_username, get_user_by_id, update_user, delete_user, create_user
from app.dependencies import get_current_user, hash_password


router = APIRouter()


@router.post("/user", response_model=User, summary="Create user")
async def create_user(user: User):
    if await get_user_by_username(user.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    group = user.group if user.group else "user"
    new_user = await create_user(name=user.name, password=hash_password(user.password), group=group)
    return new_user


@router.get("/user/{user_id}", response_model=User, summary="Get user")
async def get_user(user_id: int):
    result = await get_user_by_id(user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.patch("/user/{user_id}", response_model=User, summary="Update user")
async def update_user(user_id: int, user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["group"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own profile")

    existing = await get_user_by_id(user_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_none=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    updated = await update_user(user_id, update_data)
    return updated


@router.delete("/user/{user_id}", summary="Delete user")
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["group"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )

    deleted = await delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
