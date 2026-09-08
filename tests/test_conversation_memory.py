from app.agents.conversation_memory import ConversationMemory


def test_add_and_retrieve_messages():
    memory = ConversationMemory()

    memory.add_message(
        "session-1",
        "user",
        "What is HTTP 503?",
    )

    memory.add_message(
        "session-1",
        "assistant",
        "HTTP 503 indicates temporary unavailability.",
    )

    messages = memory.get_messages("session-1")

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "What is HTTP 503?"
    assert messages[1].role == "assistant"


def test_sessions_are_isolated():
    memory = ConversationMemory()

    memory.add_message(
        "session-1",
        "user",
        "Payment question",
    )

    memory.add_message(
        "session-2",
        "user",
        "Booking question",
    )

    session_one = memory.get_messages("session-1")
    session_two = memory.get_messages("session-2")

    assert len(session_one) == 1
    assert len(session_two) == 1

    assert session_one[0].content == "Payment question"
    assert session_two[0].content == "Booking question"


def test_clear_session():
    memory = ConversationMemory()

    memory.add_message(
        "session-1",
        "user",
        "Hello",
    )

    memory.clear_session("session-1")

    assert memory.get_messages("session-1") == []


def test_empty_session_id_is_rejected():
    memory = ConversationMemory()

    try:
        memory.get_messages("")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Session ID cannot be empty"


def test_empty_message_is_rejected():
    memory = ConversationMemory()

    try:
        memory.add_message(
            "session-1",
            "user",
            "",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Message content cannot be empty"