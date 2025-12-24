"""
Testes para o módulo prompt_loader.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from prompt_loader import (
    DEFAULT_SYSTEM_PROMPT,
    clear_cache,
    load_system_prompt,
)


class TestLoadSystemPrompt:
    """Testes para a função load_system_prompt."""

    def test_load_from_file(self) -> None:
        """Teste de carregamento bem-sucedido do arquivo de prompt."""
        with TemporaryDirectory() as tmpdir:
            # Criar arquivo de teste
            prompt_file = Path(tmpdir) / "test_prompt.md"
            test_content = """# Test Prompt

This is a test prompt.

It has multiple lines.

## Section

And more content.
"""
            prompt_file.write_text(test_content, encoding="utf-8")

            # Limpar cache antes do teste
            clear_cache()

            # Carregar prompt
            result = load_system_prompt(str(prompt_file))

            # Verificar resultado
            assert result is not None
            assert "test prompt" in result.lower()
            assert "Test Prompt" not in result  # Heading deve ser removido

    def test_cache_functionality(self) -> None:
        """Teste de cache - múltiplas chamadas não releem arquivo."""
        with TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "test_prompt.md"
            prompt_file.write_text("# Prompt\nTest content")

            clear_cache()

            # Primeira chamada
            result1 = load_system_prompt(str(prompt_file))

            # Modificar arquivo
            prompt_file.write_text("# Prompt\nModified content")

            # Segunda chamada - deve retornar cache (conteúdo antigo)
            result2 = load_system_prompt(str(prompt_file))

            # Ambas devem ser idênticas (cache funciona)
            assert result1 == result2
            assert "Modified" not in result2

    def test_file_not_found_fallback(self) -> None:
        """Teste de fallback quando arquivo não existe."""
        clear_cache()

        # Tentar carregar arquivo inexistente
        result = load_system_prompt("nonexistent/file.md")

        # Deve retornar prompt padrão
        assert result == DEFAULT_SYSTEM_PROMPT

    def test_empty_file_fallback(self) -> None:
        """Teste de fallback para arquivo vazio."""
        with TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "empty.md"
            prompt_file.write_text("", encoding="utf-8")

            clear_cache()

            # Carregar arquivo vazio
            result = load_system_prompt(str(prompt_file))

            # Deve retornar prompt padrão
            assert result == DEFAULT_SYSTEM_PROMPT

    def test_only_heading_fallback(self) -> None:
        """Teste de fallback para arquivo com apenas heading."""
        with TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "heading_only.md"
            prompt_file.write_text("# Only Heading\n", encoding="utf-8")

            clear_cache()

            # Carregar arquivo com apenas heading
            result = load_system_prompt(str(prompt_file))

            # Deve retornar prompt padrão
            assert result == DEFAULT_SYSTEM_PROMPT

    def test_valid_system_prompt_file(self) -> None:
        """Teste com arquivo de prompt do sistema real."""
        # Assumir que prompts/system_prompt.md existe
        prompt_file = "prompts/system_prompt.md"

        if not Path(prompt_file).exists():
            pytest.skip(f"Arquivo {prompt_file} não encontrado")

        clear_cache()

        result = load_system_prompt(prompt_file)

        # Deve carregar conteúdo válido
        assert result is not None
        assert len(result) > 0
        assert "Sherlock" in result or "assistente" in result.lower()

    def test_multiline_content_preservation(self) -> None:
        """Teste de preservação de conteúdo multilinhas."""
        with TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "multiline.md"
            test_content = """# Sherlock Prompt

Line one
Line two
Line three

## Instructions

- Point 1
- Point 2
- Point 3
"""
            prompt_file.write_text(test_content, encoding="utf-8")

            clear_cache()

            result = load_system_prompt(str(prompt_file))

            # Verificar que linhas foram preservadas
            lines = result.split("\n")
            assert len(lines) > 0
            # Conteúdo relevante deve estar presente
            assert any("Line" in line for line in lines)

    def test_clear_cache(self) -> None:
        """Teste de limpeza do cache."""
        with TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "test.md"
            prompt_file.write_text("# Test\nContent")

            clear_cache()

            # Primeira carga
            result1 = load_system_prompt(str(prompt_file))

            # Limpar cache
            clear_cache()

            # Modificar arquivo
            prompt_file.write_text("# Test\nNew Content")

            # Segunda carga - deve ler novo arquivo
            result2 = load_system_prompt(str(prompt_file))

            # Após clear_cache, deve ter novo conteúdo
            assert result1 != result2
            assert "New Content" in result2


class TestDefaultPrompt:
    """Testes para o prompt padrão."""

    def test_default_prompt_is_not_empty(self) -> None:
        """Teste que o prompt padrão não é vazio."""
        assert DEFAULT_SYSTEM_PROMPT is not None
        assert len(DEFAULT_SYSTEM_PROMPT) > 0

    def test_default_prompt_contains_sherlock(self) -> None:
        """Teste que o prompt padrão menciona Sherlock."""
        assert "Sherlock" in DEFAULT_SYSTEM_PROMPT
        assert "português" in DEFAULT_SYSTEM_PROMPT.lower()
