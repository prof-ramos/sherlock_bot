"""
Configurações compartilhadas para testes do pytest.
"""

import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set environment variables for test collection (must be valid length for Pydantic validation)
os.environ["DISCORD_TOKEN"] = "a" * 50  # Minimum 50 characters required by validation
os.environ["OPENROUTER_API_KEY"] = "b" * 50  # Minimum 50 characters required by validation
os.environ["AI_MODEL"] = "test/model"


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Fixture providing a temporary test database path."""
    return tmp_path / "test_sherlock.db"


@pytest.fixture
def mock_discord_message() -> MagicMock:
    """Fixture providing a mock Discord message."""
    message = MagicMock()
    message.author.id = 123456789
    message.author.name = "TestUser"
    message.channel.id = 987654321
    message.content = "Test message"
    message.reply = AsyncMock()
    return message


@pytest.fixture
def mock_discord_interaction() -> MagicMock:
    """Fixture providing a mock Discord interaction for slash commands."""
    interaction = MagicMock()
    interaction.user.id = 123456789
    interaction.user.name = "TestUser"
    interaction.channel.id = 987654321
    interaction.response.send_message = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction


@pytest.fixture
def mock_openai_client() -> AsyncMock:
    """Fixture providing a mock OpenAI client."""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock(
        return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="AI response test message"))]
        )
    )
    return client


@pytest.fixture
def env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture to set required environment variables for tests."""
    monkeypatch.setenv("DISCORD_TOKEN", "test_token_12345")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key_67890")
    monkeypatch.setenv("AI_MODEL", "anthropic/claude-3.5-sonnet")


@pytest.fixture
def cleanup_database(test_db_path: Path) -> Generator[None, None, None]:
    """Fixture to clean up test database after tests."""
    yield
    if test_db_path.exists():
        test_db_path.unlink()


# Removed redundant reset_env fixture that conflicted with env_vars
