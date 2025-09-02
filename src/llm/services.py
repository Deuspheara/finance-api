from uuid import UUID

from src.core.database import get_session
from src.llm.clients import OpenRouterClient
from src.llm.models import ConversationLog


class LLMService:
    def __init__(self) -> None:
        self.client: OpenRouterClient = OpenRouterClient()
        self.conversation_contexts: dict[UUID, list[dict[str, str]]] = {}

    async def generate_response(self, user_id: UUID, message: str) -> str:
        # Get or create conversation context
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = []

        context = self.conversation_contexts[user_id]
        context.append({"role": "user", "content": message})

        # Send to LLM
        response_content = await self.client.send_message(context)

        # Add response to context
        context.append({"role": "assistant", "content": response_content})

        # Log to database
        async for session in get_session():
            log_entry = ConversationLog(
                user_id=user_id, message=message, response=response_content
            )
            session.add(log_entry)
            await session.commit()
            break

        return response_content
