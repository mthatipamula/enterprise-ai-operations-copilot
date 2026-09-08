from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models.conversation import ConversationMessage


class ConversationRepository:
    """
    Persistence layer for conversation messages.

    Keeps PostgreSQL/SQLAlchemy details out of the Operations Agent.
    """

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> ConversationMessage:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        if not role.strip():
            raise ValueError("Role cannot be empty")

        if not content.strip():
            raise ValueError("Message content cannot be empty")

        with SessionLocal() as session:
            message = ConversationMessage(
                session_id=session_id,
                role=role,
                content=content,
            )

            session.add(message)
            session.commit()
            session.refresh(message)

            return message

    def get_messages(
        self,
        session_id: str,
    ) -> list[ConversationMessage]:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        with SessionLocal() as session:
            statement = (
                select(ConversationMessage)
                .where(
                    ConversationMessage.session_id == session_id
                )
                .order_by(ConversationMessage.created_at)
            )

            messages = session.scalars(statement).all()

            return list(messages)

    def clear_session(self, session_id: str) -> None:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        with SessionLocal() as session:
            statement = delete(ConversationMessage).where(
                ConversationMessage.session_id == session_id
            )

            session.execute(statement)
            session.commit()