from openai import AsyncOpenAI
from src.core.config import settings

class OpenRouterClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

    async def send_message(self, messages: list[dict]) -> str:
        response = await self.client.chat.completions.create(
            model=settings.DEFAULT_LLM_MODEL,
            messages=messages
        )
        return response.choices[0].message.content