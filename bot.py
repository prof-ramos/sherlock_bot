"""
Sherlock Bot - Chatbot Discord com IA via OpenRouter

Responde em 3 cenários:
1. Slash command /ia
2. Menções diretas ao bot (@bot)
3. Mensagens diretas (DMs)
"""

import asyncio
from dataclasses import dataclass

import discord
from discord import app_commands
from discord.ext import commands
from openai import APIConnectionError, AsyncOpenAI, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import settings
from database import (
    add_message,
    clear_user_history,
    get_context_messages,
    get_user_stats,
    init_db,
)
from logger import logger
from prompt_loader import load_system_prompt
from rate_limiter import rate_limit


class EmptyAIResponseError(Exception):
    """Exceção levantada quando a IA retorna uma resposta vazia."""

    pass


# Cliente OpenRouter (compatível com OpenAI)
# Configuração é validada automaticamente via config.py
openai_client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
)

# Carregar system prompt na inicialização (cache global)
SYSTEM_PROMPT = load_system_prompt()

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True  # Para ler conteúdo de mensagens (menções/DMs)
intents.dm_messages = True  # Para receber DMs

# Inicializar bot
bot = commands.Bot(command_prefix="!", intents=intents)


# =============================================================================
# Dataclass para resposta estruturada
# =============================================================================
@dataclass
class AIResponse:
    """Resposta estruturada da IA."""

    content: str
    tokens_prompt: int = 0
    tokens_completion: int = 0
    model: str = ""

    @property
    def tokens_total(self) -> int:
        """Total de tokens consumidos."""
        return self.tokens_prompt + self.tokens_completion


# =============================================================================
# Chamada à API com retry
# =============================================================================
@retry(
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def chamar_ia(messages: list[dict]) -> AIResponse:
    """
    Chama a API OpenRouter com retry automático para erros transientes.

    Args:
        messages: Lista de mensagens no formato OpenAI

    Returns:
        AIResponse com conteúdo e métricas de tokens

    Raises:
        RateLimitError: Após 3 tentativas com rate limit
        APIConnectionError: Após 3 tentativas com erro de conexão
        asyncio.TimeoutError: Se a requisição exceder o tempo limite
    """
    try:
        async with asyncio.timeout(settings.request_timeout_seconds):
            response = await openai_client.chat.completions.create(
                model=settings.ai_model,
                messages=messages,  # type: ignore
            )

        if not response.choices:
            raise EmptyAIResponseError("API retornou uma lista de escolhas vazia.")

        usage = response.usage
        return AIResponse(
            content=response.choices[0].message.content or "",
            tokens_prompt=usage.prompt_tokens if usage else 0,
            tokens_completion=usage.completion_tokens if usage else 0,
            model=response.model,
        )
    except TimeoutError:
        logger.error(f"Timeout de {settings.request_timeout_seconds}s atingido na chamada da IA")
        raise


# =============================================================================
# Função centralizada para processar IA
# =============================================================================
async def processar_ia(conteudo: str, user_id: int, channel_id: int) -> str:
    """
    Envia pergunta para a IA usando histórico como contexto.

    Args:
        conteudo: Texto da pergunta do usuário
        user_id: ID do usuário Discord
        channel_id: ID do canal/DM

    Returns:
        Resposta da IA ou mensagem de erro
    """
    if not conteudo.strip():
        return "🤔 Por favor, envie uma pergunta para eu responder!"

    try:
        # Buscar histórico de contexto (sem salvar a mensagem atual ainda)
        context_messages = get_context_messages(user_id, channel_id)

        # Montar mensagens com system prompt + histórico + mensagem atual
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            *context_messages,
            {"role": "user", "content": conteudo},
        ]

        # Chamar IA com retry automático
        ai_response = await chamar_ia(messages)
        resposta = ai_response.content or "🤷 Não consegui gerar uma resposta."

        # Salvar ambas as mensagens no histórico apenas após o sucesso
        add_message(user_id, channel_id, "user", conteudo)
        add_message(user_id, channel_id, "assistant", resposta)

        # Log de tokens
        if ai_response.tokens_total > 0:
            logger.debug(
                f"Tokens consumidos: {ai_response.tokens_total}",
                extra={
                    "tokens_prompt": ai_response.tokens_prompt,
                    "tokens_completion": ai_response.tokens_completion,
                    "model": ai_response.model,
                    "user_id": user_id,
                },
            )

        return resposta

    except RateLimitError:
        return "⚠️ Muitas requisições. Aguarde alguns segundos e tente novamente."
    except APIConnectionError:
        return "⚠️ Erro de conexão com a IA. Tente novamente em instantes."
    except TimeoutError:
        return "⚠️ A IA demorou muito para responder. Tente novamente."
    except EmptyAIResponseError:
        return "⚠️ A IA retornou uma resposta vazia. Tente novamente."
    except Exception as e:
        return f"❌ Erro ao processar: {e!s}"


async def enviar_resposta(
    destino: discord.Interaction | discord.Message,
    resposta: str,
) -> None:
    """
    Envia resposta dividindo em chunks se necessário (limite Discord: 2000 chars).

    Args:
        destino: Interaction (slash) ou Message (menção/DM)
        resposta: Texto da resposta
    """
    # Dividir em chunks de 2000 caracteres
    chunks = [resposta[i : i + 2000] for i in range(0, len(resposta), 2000)]

    if isinstance(destino, discord.Interaction):
        # Slash command - usar followup
        for i, chunk in enumerate(chunks):
            if i == 0:
                await destino.followup.send(chunk)
            else:
                await destino.followup.send(chunk)
    else:
        # Mensagem (menção/DM) - usar reply
        for i, chunk in enumerate(chunks):
            if i == 0:
                await destino.reply(chunk)
            else:
                await destino.channel.send(chunk)


# =============================================================================
# Eventos do Bot
# =============================================================================
@bot.event
async def on_ready() -> None:
    """Executado quando o bot está pronto."""
    logger.info(
        "Bot está online",
        extra={"bot_id": bot.user.id if bot.user else None, "bot_name": str(bot.user)},
    )
    logger.info(
        f"Modelo de IA configurado: {settings.ai_model}",
        extra={"model": settings.ai_model},
    )
    logger.info("Sincronizando slash commands...")

    try:
        synced = await bot.tree.sync()
        logger.info(
            "Slash commands sincronizados",
            extra={"count": len(synced), "commands": [cmd.name for cmd in synced]},
        )
    except Exception as e:
        logger.error(
            "Erro ao sincronizar comandos",
            extra={"error": str(e)},
        )


# =============================================================================
# SLASH COMMAND /ia
# =============================================================================
@bot.tree.command(name="ia", description="Faça uma pergunta para a IA")
@app_commands.describe(pergunta="Sua pergunta para a IA")
@rate_limit
async def slash_ia(interaction: discord.Interaction, pergunta: str) -> None:
    """Slash command para interagir com a IA."""
    await interaction.response.defer(thinking=True)
    logger.info(
        "Comando /ia recebido",
        extra={"user_id": interaction.user.id, "question_length": len(pergunta)},
    )

    resposta = await processar_ia(
        pergunta,
        user_id=interaction.user.id,
        channel_id=interaction.channel_id or interaction.user.id,
    )
    await enviar_resposta(interaction, resposta)


# =============================================================================
# SLASH COMMAND /limpar - Limpar histórico
# =============================================================================
@bot.tree.command(name="limpar", description="Limpa seu histórico de conversas")
async def slash_limpar(interaction: discord.Interaction) -> None:
    """Limpa o histórico do usuário no canal atual."""
    channel_id = interaction.channel_id or interaction.user.id
    logger.info(
        "Comando /limpar recebido",
        extra={"user_id": interaction.user.id, "channel_id": channel_id},
    )
    removed = clear_user_history(interaction.user.id, channel_id)
    logger.info(
        "Histórico limpo",
        extra={"user_id": interaction.user.id, "messages_removed": removed},
    )
    await interaction.response.send_message(
        f"🗑️ Histórico limpo! {removed} mensagem(ns) removida(s).",
        ephemeral=True,
    )


# =============================================================================
# SLASH COMMAND /stats - Estatísticas
# =============================================================================
@bot.tree.command(name="stats", description="Mostra suas estatísticas de uso")
@rate_limit
async def slash_stats(interaction: discord.Interaction) -> None:
    """Mostra estatísticas do usuário."""
    logger.info(
        "Comando /stats recebido",
        extra={"user_id": interaction.user.id},
    )
    stats = get_user_stats(interaction.user.id)
    await interaction.response.send_message(
        f"📊 **Suas estatísticas:**\n"
        f"• Mensagens: {stats['total_messages']}\n"
        f"• Canais: {stats['total_channels']}",
        ephemeral=True,
    )


# =============================================================================
# MENÇÕES (@bot) e MENSAGENS DIRETAS (DMs)
# =============================================================================
@bot.event
async def on_message(message: discord.Message) -> None:
    """Handler para menções e DMs."""
    # Ignorar próprias mensagens
    if message.author == bot.user:
        return

    # Ignorar outros bots
    if message.author.bot:
        return

    conteudo: str | None = None
    message_type: str | None = None

    # MENSAGEM DIRETA (DM)
    if isinstance(message.channel, discord.DMChannel):
        conteudo = message.content.strip()
        message_type = "DM"

    # MENÇÃO AO BOT
    elif bot.user and bot.user.mentioned_in(message):
        # Remover menção do conteúdo
        conteudo = message.content.replace(f"<@{bot.user.id}>", "").strip()
        # Também remover menção com nickname (caso exista)
        conteudo = conteudo.replace(f"<@!{bot.user.id}>", "").strip()
        message_type = "MENTION"

    # Se tem conteúdo para processar
    if conteudo is not None:
        logger.info(
            "Mensagem recebida",
            extra={
                "user_id": message.author.id,
                "channel_id": message.channel.id,
                "type": message_type,
                "content_length": len(conteudo),
            },
        )

        # Mostrar indicador de digitação
        async with message.channel.typing():
            resposta = await processar_ia(
                conteudo,
                user_id=message.author.id,
                channel_id=message.channel.id,
            )

        await enviar_resposta(message, resposta)

    # Processar comandos de prefixo normalmente
    await bot.process_commands(message)


# =============================================================================
# Iniciar Bot
# =============================================================================
if __name__ == "__main__":
    logger.info("Iniciando Sherlock Bot...")
    logger.info(f"Configuração: {settings}")
    init_db()  # Inicializar banco de dados explicitamente
    try:
        bot.run(settings.discord_token)
    except Exception as e:
        logger.critical(
            "Erro crítico ao iniciar bot",
            extra={"error": str(e)},
        )
        raise
