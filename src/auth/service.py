from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginRequest, TokenResponse
from src.users.service import UserService
from src.core.security import verify_password, create_access_token
from src.core.config import settings
from src.core.exceptions import AuthenticationError

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session)
    
    async def authenticate_user(self, login_request: LoginRequest) -> TokenResponse:
        user = await self.user_service.get_user_by_email(login_request.email)
        
        if not user or not verify_password(login_request.password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password")
        
        if not user.is_active:
            raise AuthenticationError("User account is disabled")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )