from pydantic import BaseModel
from uuid import UUID

class LLMRequest(BaseModel):
    user_id: UUID
    message: str

class LLMResponse(BaseModel):
    response: str