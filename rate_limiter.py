"""
Rate Limiter para prevenir abuso de requisições à API.

Implementa um sistema simples baseado em memória com sliding window.
"""

import threading
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any

from discord import Interaction

from config import settings
from logger import logger


class RateLimiter:
    """Rate limiter simples baseado em memória com sliding window."""

    def __init__(self, max_requests: int, window_minutes: int = 1):
        """
        Inicializa o rate limiter.

        Args:
            max_requests: Máximo de requisições permitidas
            window_minutes: Janela de tempo em minutos
        """
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self.requests: dict[int, list[datetime]] = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, user_id: int) -> bool:
        """
        Verifica se usuário pode fazer requisição.

        Args:
            user_id: ID do usuário Discord

        Returns:
            True se requisição é permitida, False caso contrário
        """
        now = datetime.now(UTC)
        cutoff = now - self.window

        with self._lock:
            # Remove requisições antigas (fora da janela)
            self.requests[user_id] = [ts for ts in self.requests[user_id] if ts > cutoff]

            # Verifica se atingiu o limite
            if len(self.requests[user_id]) >= self.max_requests:
                return False

            # Registra nova requisição
            self.requests[user_id].append(now)
            return True

    def get_remaining(self, user_id: int) -> int:
        """
        Retorna número de requisições restantes para usuário.

        Args:
            user_id: ID do usuário Discord

        Returns:
            Número de requisições disponíveis (nunca negativo)
        """
        now = datetime.now(UTC)
        cutoff = now - self.window

        with self._lock:
            # Remove requisições antigas (fora da janela)
            self.requests[user_id] = [ts for ts in self.requests[user_id] if ts > cutoff]

            remaining = self.max_requests - len(self.requests[user_id])
            return max(0, remaining)

    def get_info(self, user_id: int) -> dict[str, Any]:
        """
        Retorna informações completas do rate limit para usuário.

        Args:
            user_id: ID do usuário Discord

        Returns:
            Dict com informações de rate limit
        """
        now = datetime.now(UTC)
        cutoff = now - self.window

        with self._lock:
            # Remove requisições antigas (fora da janela)
            self.requests[user_id] = [ts for ts in self.requests[user_id] if ts > cutoff]

            requests_made = len(self.requests[user_id])
            return {
                "user_id": user_id,
                "requests_made": requests_made,
                "requests_allowed": self.max_requests,
                "remaining": max(0, self.max_requests - requests_made),
                "window_minutes": self.window.total_seconds() / 60,
            }

    def cleanup_inactive_users(self) -> None:
        """
        Remove usuários com timestamps expirados para prevenir vazamento de memória.
        Deve ser chamado periodicamente (ex.: background thread).
        """
        now = datetime.now(UTC)
        cutoff = now - self.window

        with self._lock:
            users_to_remove = []
            for user_id, timestamps in self.requests.items():
                filtered = [ts for ts in timestamps if ts > cutoff]
                if filtered:
                    self.requests[user_id] = filtered
                else:
                    users_to_remove.append(user_id)

            for user_id in users_to_remove:
                del self.requests[user_id]


# Singleton global
rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_requests_per_minute,
)


def rate_limit(func: Callable) -> Callable:
    """
    Decorator para rate limiting em slash commands.

    Verifica se o usuário atingiu o limite de requisições por minuto.
    Se sim, envia mensagem efêmera avisando.

    Args:
        func: Função assíncrona a decorar

    Returns:
        Wrapper assíncrono com rate limiting
    """

    @wraps(func)
    async def wrapper(interaction: Interaction, *args: Any, **kwargs: Any) -> Any:
        user_id = interaction.user.id

        # Se rate limiting está desabilitado, executar normalmente
        if not settings.rate_limit_enabled:
            return await func(interaction, *args, **kwargs)

        # Verificar se requisição é permitida
        if not rate_limiter.is_allowed(user_id):
            logger.warning(
                "Rate limit acionado para usuário %s",
                user_id,
                extra={
                    "user_id": user_id,
                    "limit": settings.rate_limit_requests_per_minute,
                },
            )

            await interaction.response.send_message(
                f"⏱️ **Rate Limit Acionado**\n\n"
                f"Você atingiu o limite de **{settings.rate_limit_requests_per_minute}** "
                f"requisições por minuto.\n\n"
                f"Aguarde um pouco e tente novamente. "
                f"Seu limite será resetado em ~1 minuto.",
                ephemeral=True,
            )
            return

        # Requisição permitida - executar função original
        try:
            return await func(interaction, *args, **kwargs)
        except Exception as e:
            logger.exception(
                "Erro ao processar comando para usuário %s",
                user_id,
                extra={"user_id": user_id, "error": str(e)},
            )
            raise

    return wrapper
