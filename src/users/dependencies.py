from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_session
from src.users.service import UserService

async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)