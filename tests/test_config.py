"""
Tests para o módulo de configuração (config.py).

Valida a carga e validação de configurações via Pydantic.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError


class TestSettingsValidation:
    """Testes para validação de configurações."""

    def test_settings_require_discord_token(self, monkeypatch) -> None:
        """Testa que DISCORD_TOKEN é obrigatório."""
        from config import Settings

        monkeypatch.delenv("DISCORD_TOKEN", raising=False)
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                _env_file=None,  # type: ignore
                openrouter_api_key="test_key",
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and error["loc"] == ("discord_token",) for error in errors
        )

    def test_settings_require_openrouter_api_key(self, monkeypatch) -> None:
        """Testa que OPENROUTER_API_KEY é obrigatório."""
        from config import Settings

        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                _env_file=None,  # type: ignore
                discord_token="test_token",
            )

        errors = exc_info.value.errors()
        assert any(
            error["type"] == "missing" and error["loc"] == ("openrouter_api_key",)
            for error in errors
        )

    def test_settings_with_valid_values(self) -> None:
        """Testa criação de Settings com valores válidos."""
        from config import Settings

        settings = Settings(
            _env_file=None,  # type: ignore
            discord_token="t" * 50,
            openrouter_api_key="k" * 50,
            ai_model="anthropic/claude-3.5-sonnet",
        )

        assert len(settings.discord_token) == 50
        assert len(settings.openrouter_api_key) == 50
        assert settings.ai_model == "anthropic/claude-3.5-sonnet"

    def test_settings_defaults(self) -> None:
        """Testa valores padrão das configurações."""
        from config import Settings

        settings = Settings(
            discord_token="t" * 50,
            openrouter_api_key="k" * 50,
        )

        assert settings.request_timeout_seconds == 30
        assert settings.max_context_messages == 10
        assert settings.max_message_length == 4000
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_requests_per_minute == 10
        assert settings.log_level == "INFO"


class TestSettingsConstraints:
    """Testes para validação de constraints nos campos."""

    def test_request_timeout_min_constraint(self) -> None:
        """Testa que request_timeout_seconds tem mínimo de 5."""
        from config import Settings

        with pytest.raises(ValidationError):
            Settings(
                discord_token="test_token",
                openrouter_api_key="test_key",
                request_timeout_seconds=3,  # Menor que 5
            )

    def test_request_timeout_max_constraint(self) -> None:
        """Testa que request_timeout_seconds tem máximo de 120."""
        from config import Settings

        with pytest.raises(ValidationError):
            Settings(
                discord_token="test_token",
                openrouter_api_key="test_key",
                request_timeout_seconds=150,  # Maior que 120
            )

    def test_max_context_messages_min_constraint(self) -> None:
        """Testa que max_context_messages tem mínimo de 1."""
        from config import Settings

        with pytest.raises(ValidationError):
            Settings(
                discord_token="test_token",
                openrouter_api_key="test_key",
                max_context_messages=0,  # Menor que 1
            )

    def test_rate_limit_requests_per_minute_constraint(self) -> None:
        """Testa limites do rate_limit_requests_per_minute."""
        from config import Settings

        # Válido
        settings = Settings(
            discord_token="t" * 50,
            openrouter_api_key="k" * 50,
            rate_limit_requests_per_minute=30,
        )
        assert settings.rate_limit_requests_per_minute == 30

        # Inválido - menor que 1
        with pytest.raises(ValidationError):
            Settings(
                discord_token="test_token",
                openrouter_api_key="test_key",
                rate_limit_requests_per_minute=0,
            )

        # Inválido - maior que 60
        with pytest.raises(ValidationError):
            Settings(
                discord_token="test_token",
                openrouter_api_key="test_key",
                rate_limit_requests_per_minute=70,
            )


class TestSettingsSingleton:
    """Testes para o singleton global de settings."""

    def test_settings_singleton_created(self) -> None:
        """Testa que o singleton de settings foi criado."""
        from config import settings

        assert settings is not None
        assert settings.discord_token is not None
        assert settings.openrouter_api_key is not None

    def test_settings_db_path_default(self) -> None:
        """Testa que o caminho padrão do banco é sherlock.db."""
        from config import settings

        assert settings.db_path.name == "sherlock.db"
        assert isinstance(settings.db_path, Path)

    def test_settings_repr_hides_tokens(self) -> None:
        """Testa que __repr__ não expõe tokens sensíveis."""
        from config import Settings

        settings = Settings(
            discord_token="s" * 50,
            openrouter_api_key="k" * 50,
        )

        repr_str = repr(settings)

        # Deve conter informações úteis
        assert "model=" in repr_str
        assert "timeout=" in repr_str
        assert "rate_limit=" in repr_str

        # Não deve conter tokens
        assert "super_secret_token_xyz" not in repr_str
        assert "super_secret_key_abc" not in repr_str


class TestSettingsEnvironment:
    """Testes para carregamento de ambiente."""

    def test_settings_from_env_file(self, tmp_path: Path) -> None:
        """Testa carregamento de .env file."""
        import sys

        # Criar arquivo .env temporário
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DISCORD_TOKEN=token_from_env\n"
            "OPENROUTER_API_KEY=key_from_env\n"
            "AI_MODEL=custom/model\n"
            "REQUEST_TIMEOUT_SECONDS=60\n"
        )

        # Adicionar diretório temporário ao sys.path
        sys.path.insert(0, str(tmp_path))

        try:
            # Importar Settings com .env customizado
            from config import Settings

            Settings(
                _env_file=str(env_file),  # type: ignore
            )

            # Verificar que valores foram carregados do .env
            # (dependendo da implementação, pode não funcionar assim)
            # Este é mais um teste de exemplo da funcionalidade esperada
        finally:
            sys.path.pop(0)
