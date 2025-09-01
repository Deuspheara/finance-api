from fastapi import APIRouter, Depends, HTTPException

from src.llm.services import LLMService
from src.llm.schemas import LLMRequest, LLMResponse
from src.llm.dependencies import get_llm_service
from src.auth.dependencies import get_current_active_user
from src.users.models import User
from src.subscriptions.services import SubscriptionService
from src.subscriptions.dependencies import get_subscription_service

router = APIRouter()

@router.post("/chat", response_model=LLMResponse)
async def chat_with_llm(
    request: LLMRequest,
    current_user: User = Depends(get_current_active_user),
    llm_service: LLMService = Depends(get_llm_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    # Ensure user can only chat for themselves
    if request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot chat for another user")
    
    # Check usage limit for LLM requests
    if not await subscription_service.check_usage_limit(current_user.id, "llm_requests"):
        raise HTTPException(status_code=429, detail="Usage limit exceeded for LLM requests")
    
    # Generate response
    response_text = await llm_service.generate_response(current_user.id, request.message)
    
    # Log usage
    await subscription_service.log_usage(current_user.id, "llm_requests")
    
    return LLMResponse(response=response_text)