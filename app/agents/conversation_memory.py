from dataclasses import dataclass

from app.agents.conversation_repository import ConversationRepository


@dataclass
class ConversationMessage:
    role: str
    content: str


class ConversationMemory:
    """
    Persistent conversation memory for the Operations Agent.

    Conversation messages are stored in PostgreSQL through
    the ConversationRepository.
    """

    def __init__(self):
        self.repository = ConversationRepository()

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        if not content.strip():
            raise ValueError("Message content cannot be empty")

        self.repository.save_message(
            session_id=session_id,
            role=role,
            content=content,
        )

    def get_messages(
        self,
        session_id: str,
    ) -> list[ConversationMessage]:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        messages = self.repository.get_messages(session_id)

        return [
            ConversationMessage(
                role=message.role,
                content=message.content,
            )
            for message in messages
        ]

    def clear_session(self, session_id: str) -> None:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        self.repository.clear_session(session_id)