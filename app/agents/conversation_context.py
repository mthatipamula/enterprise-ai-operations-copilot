from app.agents.conversation_memory import ConversationMessage


def build_conversation_context(
    messages: list[ConversationMessage],
) -> str:
    """
    Convert conversation history into a readable context block
    that can be supplied to an LLM.
    """

    if not messages:
        return ""

    lines = []

    for message in messages:
        role = message.role.capitalize()
        lines.append(f"{role}: {message.content}")

    return "\n".join(lines)