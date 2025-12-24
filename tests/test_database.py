"""
Unit tests for database module.
"""

from datetime import datetime

from config import settings
from database import (
    Message,
    add_message,
    clear_user_history,
    get_connection,
    get_context_messages,
    get_conversation_history,
    get_user_stats,
    init_db,
)


class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation(self) -> None:
        """Test creating a Message instance."""
        msg = Message(
            id=1,
            user_id=123,
            channel_id=456,
            role="user",
            content="Hello",
            created_at=datetime.now(),
        )
        assert msg.id == 1
        assert msg.user_id == 123
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_to_openai_format(self) -> None:
        """Test converting Message to OpenAI format."""
        msg = Message(
            id=1,
            user_id=123,
            channel_id=456,
            role="assistant",
            content="Response text",
            created_at=datetime.now(),
        )
        openai_format = msg.to_openai_format()
        assert openai_format["role"] == "assistant"
        assert openai_format["content"] == "Response text"

    def test_message_user_role(self) -> None:
        """Test message with user role."""
        msg = Message(
            id=2,
            user_id=456,
            channel_id=789,
            role="user",
            content="User question",
            created_at=datetime.now(),
        )
        openai_format = msg.to_openai_format()
        assert openai_format["role"] == "user"
        assert openai_format["content"] == "User question"


class TestDatabaseConnection:
    """Tests for database connection management."""

    def test_get_connection_context_manager(self, test_db_path, monkeypatch) -> None:
        """Test that get_connection works as context manager."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        with get_connection() as conn:
            assert conn is not None
            assert hasattr(conn, "execute")


class TestDatabaseInit:
    """Tests for database initialization."""

    def test_init_db_creates_tables(self, test_db_path, monkeypatch) -> None:
        """Test that init_db creates required tables."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
            )
            table = cursor.fetchone()
            assert table is not None


class TestMessageOperations:
    """Tests for message storage and retrieval."""

    def test_add_message(self, test_db_path, monkeypatch) -> None:
        """Test adding a message to the database."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()

        user_id = 9999
        channel_id = 8888

        add_message(user_id, channel_id, "user", "Test message")

        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM messages WHERE user_id = ? AND channel_id = ?",
                (user_id, channel_id),
            )
            row = cursor.fetchone()
            assert row is not None
            assert row["content"] == "Test message"

    def test_add_assistant_message(self, test_db_path, monkeypatch) -> None:
        """Test adding an assistant message."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()
        user_id = 1111
        channel_id = 2222

        add_message(user_id, channel_id, "assistant", "AI response")

        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT role FROM messages WHERE user_id = ? AND content = ?",
                (user_id, "AI response"),
            )
            row = cursor.fetchone()
            assert row is not None
            assert row["role"] == "assistant"

    def test_get_context_messages(self, test_db_path, monkeypatch) -> None:
        """Test retrieving context messages."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()
        user_id = 3333
        channel_id = 4444

        add_message(user_id, channel_id, "user", "First message")
        add_message(user_id, channel_id, "assistant", "Response")

        messages = get_context_messages(user_id, channel_id)
        assert len(messages) <= settings.max_context_messages
        assert any(m["content"] == "First message" for m in messages)
        assert any(m["content"] == "Response" for m in messages)

    def test_get_conversation_history(self, test_db_path, monkeypatch) -> None:
        """Test retrieving conversation history as Message objects."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()
        user_id = 3333
        channel_id = 4444

        add_message(user_id, channel_id, "user", "First message")
        add_message(user_id, channel_id, "assistant", "Response")

        messages = get_conversation_history(user_id, channel_id)
        assert len(messages) == 2
        assert isinstance(messages[0], Message)
        assert messages[0].content == "First message"  # Mais antiga primeiro
        assert messages[1].content == "Response"

    def test_clear_user_history(self, test_db_path, monkeypatch) -> None:
        """Test clearing user's message history."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()
        user_id = 5555
        channel_id = 6666

        add_message(user_id, channel_id, "user", "Message to delete")
        clear_user_history(user_id, channel_id)

        messages = get_context_messages(user_id, channel_id)
        assert len(messages) == 0

    def test_get_user_stats(self, test_db_path, monkeypatch) -> None:
        """Test retrieving user statistics."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()
        user_id = 7777
        channel_id = 8888

        add_message(user_id, channel_id, "user", "Msg 1")
        add_message(user_id, channel_id, "assistant", "Resp 1")
        add_message(user_id, channel_id, "user", "Msg 2")

        stats = get_user_stats(user_id)
        assert stats is not None
        assert stats["total_messages"] >= 3
        assert stats["total_channels"] >= 1

    def test_context_messages_limit(self, test_db_path, monkeypatch) -> None:
        """Test that context messages respects MAX_CONTEXT_MESSAGES limit."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()
        user_id = 9999
        channel_id = 9999

        # Add more messages than MAX_CONTEXT_MESSAGES
        limit = settings.max_context_messages
        for i in range(limit + 10):
            add_message(user_id, channel_id, "user", f"Message {i}")

        messages = get_context_messages(user_id, channel_id)
        assert len(messages) <= limit
