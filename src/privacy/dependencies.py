from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.privacy.services import GDPRService


async def get_gdpr_service(session: AsyncSession = Depends(get_session)) -> GDPRService:
    return GDPRService(session)
