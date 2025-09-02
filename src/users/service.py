from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.exceptions import NotFoundError, ValidationError
from src.core.security import get_password_hash
from src.subscriptions.models import Subscription
from src.subscriptions.services import SubscriptionService
from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_create: UserCreate) -> User:
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_create.email)
        if existing_user:
            raise ValidationError("Email already registered")

        user = User(
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        if user.id is None:
            raise ValueError("User ID is required")

        # Create free subscription for the new user
        subscription_service = SubscriptionService(self.session)
        await subscription_service.create_free_tier_for_user(user.id)

        return user

    async def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Delete associated subscriptions
        from sqlalchemy import delete

        stmt = delete(Subscription).where(Subscription.user_id == user_id)  # type: ignore[arg-type]
        await self.session.execute(stmt)
        await self.session.delete(user)
        await self.session.commit()
        return True
