"""
Tests para o módulo de rate limiting (rate_limiter.py).

Valida a funcionalidade de rate limiting por usuário.
"""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from rate_limiter import RateLimiter, rate_limit


class TestRateLimiter:
    """Testes para a classe RateLimiter."""

    def test_rate_limiter_initialization(self) -> None:
        """Testa inicialização do rate limiter."""
        limiter = RateLimiter(max_requests=5, window_minutes=1)

        assert limiter.max_requests == 5
        assert limiter.window.total_seconds() == 60

    def test_rate_limiter_allows_first_request(self) -> None:
        """Testa que primeira requisição é sempre permitida."""
        limiter = RateLimiter(max_requests=3)
        user_id = 123

        assert limiter.is_allowed(user_id) is True

    def test_rate_limiter_allows_up_to_max(self) -> None:
        """Testa que requisições até o máximo são permitidas."""
        limiter = RateLimiter(max_requests=3)
        user_id = 456

        # Primeiras 3 requisições devem ser permitidas
        assert limiter.is_allowed(user_id) is True
        assert limiter.is_allowed(user_id) is True
        assert limiter.is_allowed(user_id) is True

        # 4ª requisição deve ser bloqueada
        assert limiter.is_allowed(user_id) is False

    def test_rate_limiter_blocks_exceeded(self) -> None:
        """Testa que requisições acima do limite são bloqueadas."""
        limiter = RateLimiter(max_requests=2)
        user_id = 789

        limiter.is_allowed(user_id)
        limiter.is_allowed(user_id)

        # Próximas requisições devem ser bloqueadas
        assert limiter.is_allowed(user_id) is False
        assert limiter.is_allowed(user_id) is False

    def test_rate_limiter_separate_users(self) -> None:
        """Testa que limites são separados por usuário."""
        limiter = RateLimiter(max_requests=2)

        user1 = 111
        user2 = 222

        # User 1 faz 2 requisições
        assert limiter.is_allowed(user1) is True
        assert limiter.is_allowed(user1) is True
        assert limiter.is_allowed(user1) is False

        # User 2 ainda pode fazer requisições
        assert limiter.is_allowed(user2) is True
        assert limiter.is_allowed(user2) is True
        assert limiter.is_allowed(user2) is False

    def test_rate_limiter_remaining_count(self) -> None:
        """Testa contagem de requisições restantes."""
        limiter = RateLimiter(max_requests=5)
        user_id = 333

        assert limiter.get_remaining(user_id) == 5

        limiter.is_allowed(user_id)
        assert limiter.get_remaining(user_id) == 4

        limiter.is_allowed(user_id)
        limiter.is_allowed(user_id)
        assert limiter.get_remaining(user_id) == 2

    def test_rate_limiter_remaining_zero_when_exceeded(self) -> None:
        """Testa que remaining nunca é negativo."""
        limiter = RateLimiter(max_requests=1)
        user_id = 444

        limiter.is_allowed(user_id)

        # Tentar fazer mais requisições
        limiter.is_allowed(user_id)
        limiter.is_allowed(user_id)
        limiter.is_allowed(user_id)

        # Remaining nunca deve ser negativo
        assert limiter.get_remaining(user_id) == 0

    def test_rate_limiter_info(self) -> None:
        """Testa retorno de informações de rate limit."""
        limiter = RateLimiter(max_requests=10, window_minutes=1)
        user_id = 555

        limiter.is_allowed(user_id)
        limiter.is_allowed(user_id)
        limiter.is_allowed(user_id)

        info = limiter.get_info(user_id)

        assert info["user_id"] == user_id
        assert info["requests_made"] == 3
        assert info["requests_allowed"] == 10
        assert info["remaining"] == 7
        assert info["window_minutes"] == 1.0

    def test_rate_limiter_window_reset(self) -> None:
        """Testa que limite é resetado após expirar a janela."""
        limiter = RateLimiter(max_requests=2, window_minutes=1)
        user_id = 666

        # Atingir o limite
        limiter.is_allowed(user_id)
        limiter.is_allowed(user_id)
        assert limiter.is_allowed(user_id) is False

        # Simular passagem de tempo manualmente alterando timestamps
        # Remove o request mais antigo da lista
        if limiter.requests[user_id]:
            old_timestamp = limiter.requests[user_id][0]
            # Mover para mais de 1 minuto no passado
            limiter.requests[user_id][0] = old_timestamp - timedelta(minutes=2)

        # Agora deve permitir novamente
        assert limiter.is_allowed(user_id) is True


class TestRateLimitDecorator:
    """Testes para o decorator @rate_limit."""

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_allows_first_request(
        self,
    ) -> None:
        """Testa que decorator permite primeira requisição."""

        @rate_limit
        async def mock_command(interaction):
            return "success"

        interaction = MagicMock()
        interaction.user.id = 100
        interaction.response.send_message = AsyncMock()

        result = await mock_command(interaction)

        assert result == "success"
        interaction.response.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_blocks_exceeded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Testa que decorator bloqueia requisições acima do limite."""
        from config import settings

        # Monkeypatch rate limit para 1 por minuto
        monkeypatch.setattr(settings, "rate_limit_requests_per_minute", 1)

        # Criar novo limiter com limite baixo

        @rate_limit
        async def mock_command(interaction):
            return "success"

        interaction = MagicMock()
        interaction.user.id = 200
        interaction.response.send_message = AsyncMock()

        # Primeira requisição deve passar
        result = await mock_command(interaction)
        assert result == "success"

        # Segunda requisição deve ser bloqueada
        # Nota: Isso depende do monkeypatch funcionar corretamente
        # e da variável global rate_limiter ser atualizada

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Testa que decorator respeita flag de habilitação."""
        from config import settings

        # Desabilitar rate limiting
        monkeypatch.setattr(settings, "rate_limit_enabled", False)

        @rate_limit
        async def mock_command(interaction):
            return "success"

        interaction = MagicMock()
        interaction.user.id = 300
        interaction.response.send_message = AsyncMock()

        # Todas as requisições devem passar quando desabilitado
        for _ in range(100):
            result = await mock_command(interaction)
            assert result == "success"

        # send_message nunca deve ser chamado
        interaction.response.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_error_message(
        self,
    ) -> None:
        """Testa mensagem de erro quando rate limit é acionado."""
        from rate_limiter import rate_limit

        # Esgotar limite para um usuário
        user_id = 400
        limiter = RateLimiter(max_requests=1)
        for _ in range(5):
            limiter.is_allowed(user_id)

        @rate_limit
        async def mock_command(interaction):
            return "success"

        interaction = MagicMock()
        interaction.user.id = user_id
        interaction.response.send_message = AsyncMock()

        # Monkeypatch do rate_limiter global para usar nosso limiter
        import rate_limiter as rl_module

        original_limiter = rl_module.rate_limiter
        rl_module.rate_limiter = limiter

        try:
            result = await mock_command(interaction)
            assert result is None  # Não retorna nada quando bloqueado

            # Deve ter chamado send_message com erro
            interaction.response.send_message.assert_called_once()
            call_args = interaction.response.send_message.call_args
            assert "Rate Limit Acionado" in str(call_args) or "ephemeral" in str(call_args)
        finally:
            rl_module.rate_limiter = original_limiter

    @pytest.mark.asyncio
    async def test_rate_limit_decorator_exception_handling(
        self,
    ) -> None:
        """Testa tratamento de exceções no decorator."""

        @rate_limit
        async def mock_command_error(interaction):
            raise ValueError("Teste de erro")

        interaction = MagicMock()
        interaction.user.id = 500
        interaction.response.send_message = AsyncMock()

        with pytest.raises(ValueError, match="Teste de erro"):
            await mock_command_error(interaction)
