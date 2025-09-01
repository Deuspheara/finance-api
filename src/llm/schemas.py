from uuid import UUID

from pydantic import BaseModel


class LLMRequest(BaseModel):
    user_id: UUID
    message: str

class LLMResponse(BaseModel):
    response: str
