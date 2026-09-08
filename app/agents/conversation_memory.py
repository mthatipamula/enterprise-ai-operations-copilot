from dataclasses import dataclass, field


@dataclass
class ConversationMessage:
    role: str
    content: str


class ConversationMemory:
    """
    In-memory conversation state for the Operations Agent.

    This implementation is intentionally simple for the POC.
    A production implementation can use Redis or another
    persistent/session-oriented store.
    """

    def __init__(self):
        self._sessions: dict[str, list[ConversationMessage]] = {}

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

        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append(
            ConversationMessage(
                role=role,
                content=content,
            )
        )

    def get_messages(
        self,
        session_id: str,
    ) -> list[ConversationMessage]:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        return self._sessions.get(session_id, []).copy()

    def clear_session(self, session_id: str) -> None:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        self._sessions.pop(session_id, None)