"""
Configuração centralizada do Sherlock Bot com Pydantic.

Valida automaticamente variáveis de ambiente e fornece valores padrão sensatos.
"""

from pathlib import Path

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações globais do Sherlock Bot."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # =========================================================================
    # Discord
    # =========================================================================
    discord_token: str = Field(
        ...,
        min_length=50,
        description="Token do bot Discord (obrigatório)",
    )

    # =========================================================================
    # OpenRouter / OpenAI
    # =========================================================================
    openrouter_api_key: str = Field(
        ...,
        min_length=50,
        description="API key do OpenRouter (obrigatório)",
    )

    ai_model: str = Field(
        default="anthropic/claude-3.5-sonnet",
        description="Modelo de IA a usar via OpenRouter",
    )

    # =========================================================================
    # Timeouts e Limites
    # =========================================================================
    request_timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout para chamadas da IA (5-120s)",
    )

    max_context_messages: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Número máximo de mensagens de contexto",
    )

    max_message_length: int = Field(
        default=4000,
        ge=1000,
        le=8000,
        description="Comprimento máximo de mensagem para enviar",
    )

    # =========================================================================
    # Database
    # =========================================================================
    db_path: Path = Field(
        default_factory=lambda: Path(__file__).parent / "sherlock.db",
        description="Caminho do arquivo SQLite",
    )

    # =========================================================================
    # Rate Limiting
    # =========================================================================
    rate_limit_enabled: bool = Field(
        default=True,
        description="Habilitar rate limiting por usuário",
    )

    rate_limit_requests_per_minute: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Máximo de requisições por minuto por usuário",
    )

    # =========================================================================
    # Logging
    # =========================================================================
    log_level: str = Field(
        default="INFO",
        description="Nível de logging (DEBUG, INFO, WARNING, ERROR)",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida se o nível de logging é válido."""
        allowed = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if v.upper() not in allowed:
            raise ValueError(f"log_level deve ser um de {allowed}")
        return v.upper()

    def __repr__(self) -> str:
        """Representação segura sem expor tokens."""
        return (
            f"Settings("
            f"model={self.ai_model}, "
            f"timeout={self.request_timeout_seconds}s, "
            f"rate_limit={self.rate_limit_requests_per_minute}/min"
            f")"
        )


# Singleton global - criado na importação
# Lança ValueError se variáveis obrigatórias faltam
try:
    settings = Settings()  # type: ignore
except (ValueError, ValidationError) as e:
    raise RuntimeError(
        f"❌ Erro ao carregar configuração: {e}\n"
        f"Verifique que DISCORD_TOKEN e OPENROUTER_API_KEY estão em .env "
        f"e que os valores são válidos."
    ) from e
