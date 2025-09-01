from fastapi import APIRouter, Depends

from src.auth.dependencies import get_auth_service, get_current_active_user
from src.auth.schemas import LoginRequest, TokenResponse
from src.auth.service import AuthService
from src.users.models import User
from src.users.schemas import UserResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.authenticate_user(login_request)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return UserResponse.model_validate(current_user)
