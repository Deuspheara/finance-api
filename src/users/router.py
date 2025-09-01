from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from src.users.service import UserService
from src.users.schemas import UserCreate, UserResponse, UserUpdate
from src.users.dependencies import get_user_service

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    service: UserService = Depends(get_user_service)
):
    user = await service.create_user(user_create)
    return UserResponse.model_validate(user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    user = await service.update_user(user_id, user_update)
    return UserResponse.model_validate(user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}