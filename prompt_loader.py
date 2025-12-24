"""
Carregador de prompts do sistema para o Sherlock Bot.

Responsável por:
- Carregar prompts de arquivos Markdown
- Manter cache em memória para performance
- Fornecer fallback em caso de erro
"""

from pathlib import Path

from logger import logger

# Cache global para o prompt do sistema
_SYSTEM_PROMPT_CACHE: str | None = None

# Prompt padrão como fallback
DEFAULT_SYSTEM_PROMPT = (
    "Você é Sherlock, um assistente inteligente e prestativo. "
    "Responda de forma clara, concisa e amigável em português brasileiro. "
    "Você tem acesso ao histórico da conversa para manter contexto."
)


def load_system_prompt(
    prompt_file: str = "prompts/system_prompt.md",
) -> str:
    """
    Carrega o system prompt de um arquivo Markdown.

    Usa cache global para evitar leitura repetida do disco.
    Em caso de erro, retorna prompt padrão.

    Args:
        prompt_file: Caminho do arquivo de prompt
                    (padrão: prompts/system_prompt.md)

    Returns:
        Conteúdo do prompt como string (extraído do Markdown)

    Raises:
        Nenhuma exceção é lançada. Retorna fallback em caso de erro.
    """
    global _SYSTEM_PROMPT_CACHE

    # Retornar cache se já foi carregado
    if _SYSTEM_PROMPT_CACHE is not None:
        return _SYSTEM_PROMPT_CACHE

    try:
        prompt_path = Path(prompt_file)

        # Verificar se arquivo existe
        if not prompt_path.exists():
            logger.warning(
                f"Arquivo de prompt não encontrado: {prompt_file}. Usando prompt padrão."
            )
            _SYSTEM_PROMPT_CACHE = DEFAULT_SYSTEM_PROMPT
            return _SYSTEM_PROMPT_CACHE

        # Ler arquivo
        content = prompt_path.read_text(encoding="utf-8")

        # Extrair conteúdo (remover heading do Markdown)
        lines = content.strip().split("\n")
        prompt_lines = []
        skip_heading = True

        for line in lines:
            # Pular heading inicial e linhas vazias após heading
            if skip_heading:
                if line.startswith("#"):
                    skip_heading = False
                    continue
                continue

            # Adicionar linhas relevantes (não vazias ou seções)
            if line.strip():
                prompt_lines.append(line)

        # Juntar com quebras de linha e limpar espaços extras
        final_prompt = "\n".join(prompt_lines).strip()

        if not final_prompt:
            logger.warning("Prompt carregado está vazio. Usando prompt padrão.")
            _SYSTEM_PROMPT_CACHE = DEFAULT_SYSTEM_PROMPT
            return _SYSTEM_PROMPT_CACHE

        _SYSTEM_PROMPT_CACHE = final_prompt
        logger.info(f"System prompt carregado com sucesso de {prompt_file}")
        return _SYSTEM_PROMPT_CACHE

    except OSError as e:
        logger.error(f"Erro ao ler arquivo de prompt {prompt_file}: {e}. Usando prompt padrão.")
        _SYSTEM_PROMPT_CACHE = DEFAULT_SYSTEM_PROMPT
        return _SYSTEM_PROMPT_CACHE


def clear_cache() -> None:
    """
    Limpa o cache de prompt.

    Útil para testes ou quando o arquivo é modificado em tempo de execução.
    """
    global _SYSTEM_PROMPT_CACHE
    _SYSTEM_PROMPT_CACHE = None
    logger.debug("Cache de prompt foi limpo")
