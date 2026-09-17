from fastapi import APIRouter, HTTPException, status
from app.schemas import LoginRequest, LoginResponse
from app.dependencies import get_user_by_username
from app.dependencies import verify_password, create_token


router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="Login")
async def login(login_data: LoginRequest):
    user = await get_user_by_username(login_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_token(user["name"], user["group"])
    return LoginResponse(token=token, expires_in=48 * 3600)
