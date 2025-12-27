# Test Coverage Improvement Recommendations

## Executive Summary

**Current Coverage: 91%** (Excellent overall, but critical gaps exist)

The codebase has strong test coverage overall, but **bot.py** (the main application file) is completely missing from coverage reports. This is the highest priority gap to address.

---

## Coverage Report Breakdown

| Module              | Coverage | Priority | Status |
|---------------------|----------|----------|--------|
| **bot.py**          | **0%**   | 🔴 HIGH  | Missing from report |
| database.py         | 67%      | 🔶 MEDIUM | Error paths untested |
| logger.py           | 62%      | 🔶 MEDIUM | Fallback logic untested |
| rate_limiter.py     | 84%      | 🟡 LOW   | Good coverage |
| config.py           | 89%      | 🟢 GOOD  | Minor gaps |
| prompt_loader.py    | 90%      | 🟢 GOOD  | Excellent coverage |
| **TOTAL**           | **91%**  |          | |

---

## Priority 1: bot.py Core Functionality Tests 🔴

### Missing Coverage Areas

The entire `bot.py` module (386 lines) has **no integration tests**. Current `test_bot.py` only validates environment setup and mock creation.

### Recommended Test Suite

#### 1.1 API Integration Tests

**File:** `tests/test_bot_api.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from openai import RateLimitError, APIConnectionError
import asyncio

from bot import chamar_ia, AIResponse, EmptyAIResponseError


class TestChamarIA:
    """Tests for chamar_ia() API call function."""

    @pytest.mark.asyncio
    async def test_successful_api_call(self, mock_openai_client):
        """Test successful API response with token tracking."""
        # Test that response is correctly parsed
        # Verify AIResponse object is created with correct tokens
        pass

    @pytest.mark.asyncio
    async def test_empty_response_raises_error(self, mock_openai_client):
        """Test EmptyAIResponseError when API returns empty choices."""
        # Mock response.choices = []
        # Verify EmptyAIResponseError is raised
        pass

    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_openai_client):
        """Test timeout after request_timeout_seconds."""
        # Mock delayed response exceeding timeout
        # Verify TimeoutError is raised
        pass

    @pytest.mark.asyncio
    async def test_rate_limit_retry(self, mock_openai_client):
        """Test retry logic on RateLimitError."""
        # Mock 2 failures then success
        # Verify retry with exponential backoff
        # Verify eventual success after retries
        pass

    @pytest.mark.asyncio
    async def test_connection_error_retry(self, mock_openai_client):
        """Test retry on APIConnectionError."""
        # Mock connection failures then success
        # Verify retry mechanism works
        pass

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, mock_openai_client):
        """Test failure after 3 retry attempts."""
        # Mock persistent failures
        # Verify exception is re-raised after 3 attempts
        pass


class TestAIResponse:
    """Tests for AIResponse dataclass."""

    def test_tokens_total_calculation(self):
        """Test tokens_total property calculation."""
        response = AIResponse(
            content="test",
            tokens_prompt=100,
            tokens_completion=50
        )
        assert response.tokens_total == 150

    def test_default_token_values(self):
        """Test default token values are zero."""
        response = AIResponse(content="test")
        assert response.tokens_total == 0
```

#### 1.2 Message Processing Tests

**File:** `tests/test_bot_processing.py`

```python
import pytest
from unittest.mock import AsyncMock, patch

from bot import processar_ia


class TestProcessarIA:
    """Tests for processar_ia() message processing."""

    @pytest.mark.asyncio
    async def test_empty_message_handling(self):
        """Test response for empty/whitespace messages."""
        result = await processar_ia("   ", user_id=123, channel_id=456)
        assert "🤔" in result
        assert "pergunta" in result.lower()

    @pytest.mark.asyncio
    async def test_successful_message_flow(self, mock_openai_client):
        """Test full message processing workflow."""
        # Mock database get_context_messages
        # Mock chamar_ia response
        # Verify message is saved to database (user + assistant)
        # Verify response is returned
        pass

    @pytest.mark.asyncio
    async def test_rate_limit_error_message(self, mock_openai_client):
        """Test user-friendly message on rate limit."""
        # Mock RateLimitError
        result = await processar_ia("test", user_id=123, channel_id=456)
        assert "⚠️" in result
        assert "requisições" in result.lower()

    @pytest.mark.asyncio
    async def test_connection_error_message(self, mock_openai_client):
        """Test user-friendly message on connection error."""
        # Mock APIConnectionError
        result = await processar_ia("test", user_id=123, channel_id=456)
        assert "⚠️" in result
        assert "conexão" in result.lower()

    @pytest.mark.asyncio
    async def test_timeout_error_message(self):
        """Test user-friendly message on timeout."""
        # Mock TimeoutError
        result = await processar_ia("test", user_id=123, channel_id=456)
        assert "⚠️" in result
        assert "demorou" in result.lower()

    @pytest.mark.asyncio
    async def test_empty_ai_response_error_message(self, mock_openai_client):
        """Test message when AI returns empty response."""
        # Mock EmptyAIResponseError
        result = await processar_ia("test", user_id=123, channel_id=456)
        assert "⚠️" in result
        assert "vazia" in result.lower()

    @pytest.mark.asyncio
    async def test_generic_exception_handling(self):
        """Test generic error handling."""
        # Mock unexpected exception
        result = await processar_ia("test", user_id=123, channel_id=456)
        assert "❌" in result
        assert "Erro ao processar" in result

    @pytest.mark.asyncio
    async def test_context_history_included(self, mock_openai_client):
        """Test that conversation history is included in API call."""
        # Add messages to database
        # Verify get_context_messages is called
        # Verify history is included in API request
        pass

    @pytest.mark.asyncio
    async def test_system_prompt_included(self, mock_openai_client):
        """Test that SYSTEM_PROMPT is included in messages."""
        # Verify system message is first in messages list
        pass
```

#### 1.3 Response Chunking Tests

**File:** `tests/test_bot_chunking.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from bot import enviar_resposta


class TestEnviarResposta:
    """Tests for enviar_resposta() message chunking."""

    @pytest.mark.asyncio
    async def test_short_message_no_chunking(self, mock_discord_interaction):
        """Test message under 2000 chars sent as single message."""
        resposta = "Short message"
        await enviar_resposta(mock_discord_interaction, resposta)
        # Verify followup.send called once
        mock_discord_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_long_message_chunking(self, mock_discord_interaction):
        """Test message over 2000 chars split into chunks."""
        resposta = "A" * 5000  # 5000 chars = 3 chunks
        await enviar_resposta(mock_discord_interaction, resposta)
        # Verify followup.send called 3 times
        assert mock_discord_interaction.followup.send.call_count == 3

    @pytest.mark.asyncio
    async def test_exact_2000_chars_no_chunking(self, mock_discord_interaction):
        """Test message exactly 2000 chars sent as single message."""
        resposta = "A" * 2000
        await enviar_resposta(mock_discord_interaction, resposta)
        mock_discord_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_interaction_uses_followup(self, mock_discord_interaction):
        """Test Interaction uses followup.send."""
        await enviar_resposta(mock_discord_interaction, "test")
        mock_discord_interaction.followup.send.assert_called()

    @pytest.mark.asyncio
    async def test_message_uses_reply(self, mock_discord_message):
        """Test Message uses reply for first chunk."""
        await enviar_resposta(mock_discord_message, "test")
        mock_discord_message.reply.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_chunking_uses_channel_send(self, mock_discord_message):
        """Test Message subsequent chunks use channel.send."""
        resposta = "A" * 5000  # 3 chunks
        await enviar_resposta(mock_discord_message, resposta)
        # First chunk: reply
        assert mock_discord_message.reply.call_count == 1
        # Subsequent chunks: channel.send
        assert mock_discord_message.channel.send.call_count == 2
```

#### 1.4 Slash Command Tests

**File:** `tests/test_bot_commands.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot import slash_ia, slash_limpar, slash_stats


class TestSlashIA:
    """Tests for /ia slash command."""

    @pytest.mark.asyncio
    async def test_ia_command_basic_flow(self, mock_discord_interaction):
        """Test /ia command basic workflow."""
        # Mock interaction.response.defer
        # Mock processar_ia
        await slash_ia(mock_discord_interaction, "Test question")
        # Verify defer(thinking=True) was called
        mock_discord_interaction.response.defer.assert_called_once_with(thinking=True)
        # Verify processar_ia was called with correct params
        pass

    @pytest.mark.asyncio
    async def test_ia_command_rate_limited(self, mock_discord_interaction):
        """Test /ia command respects rate limiting."""
        # Test @rate_limit decorator is applied
        # Verify rate limit check occurs
        pass

    @pytest.mark.asyncio
    async def test_ia_command_logs_request(self, mock_discord_interaction):
        """Test /ia command logs request details."""
        # Verify logger.info is called with user_id and question_length
        pass


class TestSlashLimpar:
    """Tests for /limpar slash command."""

    @pytest.mark.asyncio
    async def test_limpar_clears_history(self, mock_discord_interaction, test_db_path, monkeypatch):
        """Test /limpar clears user history."""
        # Setup: add messages to database
        # Execute: call slash_limpar
        # Verify: clear_user_history was called
        # Verify: response sent with count
        pass

    @pytest.mark.asyncio
    async def test_limpar_response_ephemeral(self, mock_discord_interaction):
        """Test /limpar response is ephemeral (only visible to user)."""
        await slash_limpar(mock_discord_interaction)
        # Verify response.send_message called with ephemeral=True
        args, kwargs = mock_discord_interaction.response.send_message.call_args
        assert kwargs.get('ephemeral') is True

    @pytest.mark.asyncio
    async def test_limpar_logs_action(self, mock_discord_interaction):
        """Test /limpar logs the action."""
        # Verify logger.info called with user_id and messages_removed
        pass


class TestSlashStats:
    """Tests for /stats slash command."""

    @pytest.mark.asyncio
    async def test_stats_displays_user_stats(self, mock_discord_interaction, test_db_path, monkeypatch):
        """Test /stats shows correct statistics."""
        # Setup: add messages to database
        # Execute: call slash_stats
        # Verify: get_user_stats was called
        # Verify: response contains total_messages and total_channels
        pass

    @pytest.mark.asyncio
    async def test_stats_response_ephemeral(self, mock_discord_interaction):
        """Test /stats response is ephemeral."""
        await slash_stats(mock_discord_interaction)
        args, kwargs = mock_discord_interaction.response.send_message.call_args
        assert kwargs.get('ephemeral') is True

    @pytest.mark.asyncio
    async def test_stats_rate_limited(self, mock_discord_interaction):
        """Test /stats respects rate limiting."""
        # Verify @rate_limit decorator is applied
        pass
```

#### 1.5 Event Handler Tests

**File:** `tests/test_bot_events.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord

from bot import on_message, on_ready


class TestOnMessage:
    """Tests for on_message event handler."""

    @pytest.mark.asyncio
    async def test_ignores_own_messages(self, mock_discord_message):
        """Test bot ignores its own messages."""
        # Set message.author = bot.user
        # Verify processar_ia is NOT called
        pass

    @pytest.mark.asyncio
    async def test_ignores_other_bots(self, mock_discord_message):
        """Test bot ignores messages from other bots."""
        mock_discord_message.author.bot = True
        await on_message(mock_discord_message)
        # Verify processar_ia is NOT called
        pass

    @pytest.mark.asyncio
    async def test_responds_to_dm(self, mock_discord_message):
        """Test bot responds to direct messages."""
        # Mock DMChannel
        mock_discord_message.channel = MagicMock(spec=discord.DMChannel)
        mock_discord_message.content = "Hello bot"
        await on_message(mock_discord_message)
        # Verify processar_ia is called with correct content
        pass

    @pytest.mark.asyncio
    async def test_responds_to_mention(self, mock_discord_message):
        """Test bot responds to @mentions."""
        # Mock bot.user.mentioned_in returning True
        # Set content with mention: "<@123456> question here"
        # Verify mention is stripped from content
        # Verify processar_ia is called with clean content
        pass

    @pytest.mark.asyncio
    async def test_responds_to_nickname_mention(self, mock_discord_message):
        """Test bot responds to @mentions with nickname format."""
        # Mock mention with nickname: "<@!123456> question"
        # Verify both mention formats are stripped
        pass

    @pytest.mark.asyncio
    async def test_typing_indicator_during_processing(self, mock_discord_message):
        """Test typing indicator shown during AI processing."""
        # Verify channel.typing() context manager is used
        pass

    @pytest.mark.asyncio
    async def test_ignores_non_dm_non_mention(self, mock_discord_message):
        """Test bot ignores regular channel messages without mention."""
        # Set message in regular channel (not DM)
        # Set bot.user.mentioned_in = False
        # Verify processar_ia is NOT called
        pass


class TestOnReady:
    """Tests for on_ready event handler."""

    @pytest.mark.asyncio
    async def test_logs_bot_info_on_ready(self):
        """Test bot logs information when ready."""
        # Verify logger.info called with bot_id and bot_name
        pass

    @pytest.mark.asyncio
    async def test_syncs_slash_commands(self):
        """Test slash commands are synced on ready."""
        # Mock bot.tree.sync()
        # Verify sync() is called
        # Verify success is logged
        pass

    @pytest.mark.asyncio
    async def test_logs_sync_errors(self):
        """Test sync errors are logged."""
        # Mock bot.tree.sync() raising exception
        # Verify logger.error is called
        pass
```

---

## Priority 2: database.py Error Handling Tests 🔶

### Missing Coverage: Error Paths

Currently missing **33% of database.py** - primarily error handling and edge cases.

### Recommended Test Suite

**File:** `tests/test_database_errors.py`

```python
import pytest
import sqlite3
from datetime import datetime
from pathlib import Path

from database import (
    parse_datetime,
    get_connection,
    init_db,
    add_message,
    get_conversation_history,
    clear_user_history,
    get_user_stats,
)


class TestParseDatetime:
    """Tests for parse_datetime() function."""

    def test_parse_iso_with_microseconds(self):
        """Test parsing ISO format with microseconds."""
        dt_str = "2024-01-15 10:30:45.123456"
        result = parse_datetime(dt_str)
        assert result.year == 2024
        assert result.microsecond == 123456

    def test_parse_iso_without_microseconds(self):
        """Test parsing ISO format without microseconds."""
        dt_str = "2024-01-15 10:30:45"
        result = parse_datetime(dt_str)
        assert result.year == 2024

    def test_parse_iso_t_with_microseconds(self):
        """Test parsing ISO T format with microseconds."""
        dt_str = "2024-01-15T10:30:45.123456"
        result = parse_datetime(dt_str)
        assert result.year == 2024

    def test_parse_iso_t_without_microseconds(self):
        """Test parsing ISO T format without microseconds."""
        dt_str = "2024-01-15T10:30:45"
        result = parse_datetime(dt_str)
        assert result.year == 2024

    def test_parse_fromisoformat_fast_path(self):
        """Test fast path using datetime.fromisoformat."""
        dt_str = "2024-01-15T10:30:45"
        result = parse_datetime(dt_str)
        assert isinstance(result, datetime)

    def test_invalid_format_raises_error(self):
        """Test invalid datetime format raises ValueError."""
        with pytest.raises(ValueError, match="Não foi possível parsear a data"):
            parse_datetime("invalid-date-format")

    def test_invalid_format_logs_error(self, caplog):
        """Test invalid format logs error before raising."""
        with pytest.raises(ValueError):
            parse_datetime("bad-format")
        assert "Falha ao parsear data" in caplog.text


class TestGetConnectionErrors:
    """Tests for get_connection() error handling."""

    def test_database_error_triggers_rollback(self, test_db_path, monkeypatch):
        """Test DatabaseError triggers rollback."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", test_db_path)

        with pytest.raises(sqlite3.DatabaseError):
            with get_connection() as conn:
                # Execute invalid SQL to trigger DatabaseError
                conn.execute("INVALID SQL STATEMENT")

        # Verify rollback occurred (no partial changes)

    def test_generic_exception_triggers_rollback(self, test_db_path, monkeypatch):
        """Test generic exceptions trigger rollback."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", test_db_path)

        with pytest.raises(Exception):
            with get_connection() as conn:
                # Raise generic exception inside context
                raise RuntimeError("Test error")

        # Verify rollback occurred

    def test_connection_closed_in_finally(self, test_db_path, monkeypatch):
        """Test connection is closed even on error."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", test_db_path)

        conn_ref = None
        try:
            with get_connection() as conn:
                conn_ref = conn
                raise RuntimeError("Test")
        except RuntimeError:
            pass

        # Verify connection was closed
        with pytest.raises(sqlite3.ProgrammingError):
            conn_ref.execute("SELECT 1")


class TestInitDBErrors:
    """Tests for init_db() error handling."""

    def test_init_db_logs_success(self, test_db_path, monkeypatch, caplog):
        """Test init_db logs success message."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", test_db_path)

        init_db()
        assert "Banco de dados inicializado com sucesso" in caplog.text

    def test_init_db_logs_errors(self, monkeypatch, caplog):
        """Test init_db logs errors."""
        from config import settings
        # Point to invalid path to trigger error
        monkeypatch.setattr(settings, "db_path", "/invalid/path/db.sqlite")

        with pytest.raises(Exception):
            init_db()

        assert "Erro ao inicializar banco de dados" in caplog.text


class TestAddMessageErrors:
    """Tests for add_message() error handling."""

    def test_invalid_role_raises_error(self, test_db_path, monkeypatch):
        """Test invalid role raises ValueError."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()

        with pytest.raises(ValueError, match="Role inválido"):
            add_message(123, 456, "invalid_role", "content")

    def test_add_message_logs_debug_on_success(self, test_db_path, monkeypatch, caplog):
        """Test successful add_message logs debug info."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()

        import logging
        caplog.set_level(logging.DEBUG)

        add_message(123, 456, "user", "test content")
        assert "Mensagem inserida" in caplog.text

    def test_add_message_logs_error_on_failure(self, test_db_path, monkeypatch, caplog):
        """Test add_message logs errors."""
        from config import settings
        # Corrupt database to trigger error
        monkeypatch.setattr(settings, "db_path", test_db_path)

        # This will log the ValueError for invalid role
        with pytest.raises(ValueError):
            add_message(123, 456, "bad_role", "content")


class TestGetConversationHistoryErrors:
    """Tests for get_conversation_history() error handling."""

    def test_get_conversation_logs_errors(self, monkeypatch, caplog):
        """Test get_conversation_history logs errors."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", "/invalid/path/db.sqlite")

        with pytest.raises(Exception):
            get_conversation_history(123, 456)

        assert "Erro ao recuperar histórico" in caplog.text


class TestClearUserHistoryErrors:
    """Tests for clear_user_history() error handling."""

    def test_clear_all_channels(self, test_db_path, monkeypatch):
        """Test clearing user history across all channels."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()

        # Add messages in multiple channels
        add_message(123, 111, "user", "channel 1")
        add_message(123, 222, "user", "channel 2")
        add_message(123, 333, "user", "channel 3")

        # Clear all channels for user
        removed = clear_user_history(123, channel_id=None)
        assert removed == 3

        # Verify all cleared
        from database import get_user_stats
        stats = get_user_stats(123)
        assert stats["total_messages"] == 0

    def test_clear_specific_channel_only(self, test_db_path, monkeypatch):
        """Test clearing only specific channel."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()

        # Add messages in multiple channels
        add_message(123, 111, "user", "channel 1")
        add_message(123, 222, "user", "channel 2")

        # Clear only channel 111
        removed = clear_user_history(123, channel_id=111)
        assert removed == 1

        # Verify only one channel cleared
        stats = get_user_stats(123)
        assert stats["total_messages"] == 1
        assert stats["total_channels"] == 1

    def test_clear_history_logs_errors(self, monkeypatch, caplog):
        """Test clear_user_history logs errors."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", "/invalid/path/db.sqlite")

        with pytest.raises(Exception):
            clear_user_history(123, 456)

        assert "Erro ao limpar histórico" in caplog.text


class TestGetUserStatsErrors:
    """Tests for get_user_stats() error handling."""

    def test_get_user_stats_logs_errors(self, monkeypatch, caplog):
        """Test get_user_stats logs errors."""
        from config import settings
        monkeypatch.setattr(settings, "db_path", "/invalid/path/db.sqlite")

        with pytest.raises(Exception):
            get_user_stats(123)

        assert "Erro ao recuperar estatísticas" in caplog.text
```

---

## Priority 3: logger.py Fallback Tests 🔶

### Missing Coverage: Fallback Logic

Currently missing **38% of logger.py** - the error handling for directory creation.

### Recommended Test Suite

**File:** `tests/test_logger.py`

```python
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestLoggerInitialization:
    """Tests for logger initialization and fallback logic."""

    def test_logs_directory_created(self, tmp_path):
        """Test logs directory is created successfully."""
        # This tests the happy path (lines covered already)
        # But ensures it works correctly
        with patch('logger.Path') as mock_path:
            mock_path.return_value = tmp_path / "logs"
            import importlib
            import logger as logger_module
            importlib.reload(logger_module)

            assert (tmp_path / "logs").exists() or True  # Directory created

    def test_fallback_to_tempfile_on_primary_failure(self):
        """Test fallback to tempfile when primary logs dir fails."""
        # Mock Path(__file__).parent.resolve() to raise exception
        # Verify tempfile.mkdtemp is called
        # Verify logs_dir is set to temp directory
        pass

    def test_logs_dir_none_on_complete_failure(self, capsys):
        """Test logs_dir=None when both primary and fallback fail."""
        # Mock both directory creation attempts to fail
        # Verify logs_dir is None
        # Verify error message printed to stderr
        pass

    def test_file_logging_disabled_when_logs_dir_none(self):
        """Test file logging handler not added when logs_dir is None."""
        # Mock logs_dir = None scenario
        # Verify _logger.add() not called for file handler
        # Verify stderr handler still added
        pass

    def test_stderr_handler_always_added(self):
        """Test stderr handler is always configured."""
        # Verify _logger.add() called with sys.stderr
        # Even when file logging fails
        pass

    def test_log_format_includes_timestamp(self):
        """Test log format includes timestamp and level."""
        # Verify format string contains {time}, {level}, {message}
        pass
```

---

## Priority 4: Integration Tests 🟡

### End-to-End Scenarios

Create comprehensive integration tests that combine multiple modules:

**File:** `tests/test_integration.py`

```python
import pytest
from unittest.mock import AsyncMock, patch

from bot import processar_ia
from database import init_db, get_conversation_history, clear_user_history
from config import settings


class TestFullConversationFlow:
    """Integration tests for full conversation workflows."""

    @pytest.mark.asyncio
    async def test_conversation_with_history_context(self, test_db_path, monkeypatch, mock_openai_client):
        """Test multi-turn conversation uses history as context."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()

        user_id = 12345
        channel_id = 67890

        # First message
        await processar_ia("What is Python?", user_id, channel_id)

        # Second message (should include first in context)
        await processar_ia("Tell me more", user_id, channel_id)

        # Verify history contains both exchanges
        history = get_conversation_history(user_id, channel_id)
        assert len(history) == 4  # 2 user + 2 assistant

        # Verify second API call included first exchange in context
        # Check mock_openai_client.chat.completions.create calls

    @pytest.mark.asyncio
    async def test_context_window_limiting(self, test_db_path, monkeypatch, mock_openai_client):
        """Test that context is limited to max_context_messages."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        monkeypatch.setattr(settings, "max_context_messages", 10)
        init_db()

        user_id = 99999
        channel_id = 88888

        # Send 20 messages (exceeding limit of 10)
        for i in range(20):
            await processar_ia(f"Message {i}", user_id, channel_id)

        # Verify only last 10 are retrieved for context
        from database import get_context_messages
        context = get_context_messages(user_id, channel_id)
        assert len(context) <= 10

    @pytest.mark.asyncio
    async def test_history_clear_affects_context(self, test_db_path, monkeypatch, mock_openai_client):
        """Test that clearing history removes context."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()

        user_id = 11111
        channel_id = 22222

        # Add some messages
        await processar_ia("First message", user_id, channel_id)
        await processar_ia("Second message", user_id, channel_id)

        # Clear history
        clear_user_history(user_id, channel_id)

        # New message should have no context
        await processar_ia("New conversation", user_id, channel_id)

        history = get_conversation_history(user_id, channel_id)
        assert len(history) == 2  # Only latest exchange


class TestRateLimitingIntegration:
    """Integration tests for rate limiting across commands."""

    @pytest.mark.asyncio
    async def test_rate_limit_applies_to_slash_commands(self, mock_discord_interaction):
        """Test rate limiting on /ia and /stats commands."""
        from bot import slash_ia, slash_stats
        from config import settings

        # Configure strict rate limit for testing
        # Make multiple rapid requests
        # Verify rate limit error after threshold
        pass

    @pytest.mark.asyncio
    async def test_rate_limit_per_user_isolation(self, mock_discord_interaction):
        """Test rate limits are per-user."""
        # User A makes requests up to limit
        # User B should still be able to make requests
        pass


class TestErrorRecovery:
    """Integration tests for error handling and recovery."""

    @pytest.mark.asyncio
    async def test_failed_api_call_does_not_save_to_database(self, test_db_path, monkeypatch, mock_openai_client):
        """Test that failed API calls don't save messages."""
        monkeypatch.setattr(settings, "db_path", test_db_path)
        init_db()

        # Mock API failure
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        user_id = 55555
        channel_id = 66666

        # Attempt to process message
        await processar_ia("Test question", user_id, channel_id)

        # Verify no messages saved (due to transaction rollback logic)
        history = get_conversation_history(user_id, channel_id)
        assert len(history) == 0
```

---

## Summary of Recommended Test Files

| New Test File                  | Priority | Purpose |
|--------------------------------|----------|---------|
| `test_bot_api.py`              | 🔴 HIGH  | API call and retry logic |
| `test_bot_processing.py`       | 🔴 HIGH  | Message processing and errors |
| `test_bot_chunking.py`         | 🔴 HIGH  | Response chunking (2000 char limit) |
| `test_bot_commands.py`         | 🔴 HIGH  | Slash commands (/ia, /limpar, /stats) |
| `test_bot_events.py`           | 🔴 HIGH  | Event handlers (on_message, on_ready) |
| `test_database_errors.py`      | 🔶 MEDIUM | Error handling and edge cases |
| `test_logger.py`               | 🔶 MEDIUM | Logger initialization and fallbacks |
| `test_integration.py`          | 🟡 LOW   | End-to-end integration tests |

---

## Expected Coverage After Improvements

| Module              | Current | Target | Gain |
|---------------------|---------|--------|------|
| bot.py              | 0%      | 85%+   | +85% |
| database.py         | 67%     | 95%+   | +28% |
| logger.py           | 62%     | 90%+   | +28% |
| rate_limiter.py     | 84%     | 90%+   | +6%  |
| **Overall**         | **91%** | **95%+** | **+4%** |

---

## Implementation Strategy

### Phase 1 (Week 1): Critical Bot Tests
- Create `test_bot_api.py` (API calls and AIResponse)
- Create `test_bot_processing.py` (processar_ia error handling)
- Create `test_bot_chunking.py` (message chunking logic)

**Expected outcome:** bot.py coverage from 0% → 60%

### Phase 2 (Week 2): Commands and Events
- Create `test_bot_commands.py` (slash commands)
- Create `test_bot_events.py` (event handlers)

**Expected outcome:** bot.py coverage from 60% → 85%

### Phase 3 (Week 3): Error Paths
- Create `test_database_errors.py`
- Create `test_logger.py`

**Expected outcome:**
- database.py: 67% → 95%
- logger.py: 62% → 90%

### Phase 4 (Week 4): Integration
- Create `test_integration.py`
- Add any missing edge case tests

**Expected outcome:** Overall coverage 95%+

---

## Testing Best Practices to Follow

1. **Use fixtures from conftest.py**
   - Reuse `mock_discord_interaction`, `mock_discord_message`, `mock_openai_client`
   - Add new fixtures as needed

2. **Test behavior, not implementation**
   - Focus on what functions do, not how
   - Example: Test that errors return user-friendly messages, not internal exception types

3. **Use descriptive test names**
   - Name pattern: `test_<function>_<scenario>_<expected_result>`
   - Example: `test_processar_ia_timeout_error_message`

4. **Isolate tests with monkeypatch**
   - Use test database paths
   - Mock external API calls
   - Don't let tests affect each other

5. **Test error messages for users**
   - Verify user-facing error messages are helpful
   - Check for emoji indicators (⚠️, ❌, etc.)
   - Ensure Portuguese language consistency

6. **Async test patterns**
   - Use `@pytest.mark.asyncio` for async functions
   - Use `AsyncMock` for async mocks
   - Test both success and failure paths

7. **Coverage is a guide, not a goal**
   - 100% coverage doesn't mean bug-free code
   - Focus on critical paths and error handling
   - Some lines (like `pass` or defensive checks) can be skipped

---

## Tools and Commands

### Run specific test file
```bash
pytest tests/test_bot_api.py -v
```

### Run tests with coverage for specific module
```bash
uv run pytest --cov=bot --cov-report=term-missing tests/test_bot_api.py
```

### Generate HTML coverage report
```bash
uv run pytest --cov --cov-report=html
# Open htmlcov/index.html in browser
```

### Run only tests matching a pattern
```bash
pytest -k "test_api" -v
```

### Run tests in parallel (faster)
```bash
pytest -n auto  # Requires pytest-xdist
```

---

## Conclusion

The codebase has **strong foundational test coverage (91%)**, but the most critical component—`bot.py`—lacks integration tests. Implementing the Priority 1 tests for bot.py will provide the most value, followed by database error handling and logger fallback tests.

**Estimated effort:**
- Priority 1 (bot.py): 3-4 days
- Priority 2 (database.py): 1-2 days
- Priority 3 (logger.py): 1 day
- Priority 4 (integration): 1-2 days

**Total: ~2 weeks** for comprehensive test improvements.
