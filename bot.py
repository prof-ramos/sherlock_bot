"""
Sherlock Bot - Chatbot Discord com IA via OpenRouter

Responde em 3 cenários:
1. Slash command /ia
2. Menções diretas ao bot (@bot)
3. Mensagens diretas (DMs)
"""

import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Carregar variáveis de ambiente
load_dotenv()

# Configuração
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "anthropic/claude-3.5-sonnet")

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN não configurado no .env")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY não configurado no .env")

# Cliente OpenRouter (compatível com OpenAI)
openai_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True  # Para ler conteúdo de mensagens (menções/DMs)
intents.direct_messages = True  # Para receber DMs

# Inicializar bot
bot = commands.Bot(command_prefix="!", intents=intents)


# =============================================================================
# Função centralizada para processar IA
# =============================================================================
async def processar_ia(conteudo: str) -> str:
    """
    Envia pergunta para a IA e retorna a resposta.

    Args:
        conteudo: Texto da pergunta do usuário

    Returns:
        Resposta da IA ou mensagem de erro
    """
    if not conteudo.strip():
        return "🤔 Por favor, envie uma pergunta para eu responder!"

    try:
        response = await openai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é Sherlock, um assistente inteligente e prestativo. "
                        "Responda de forma clara, concisa e amigável em português brasileiro."
                    ),
                },
                {"role": "user", "content": conteudo},
            ],
        )
        return response.choices[0].message.content or "🤷 Não consegui gerar uma resposta."
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
    print(f"✅ Bot {bot.user} está online!")
    print(f"🤖 Modelo de IA: {AI_MODEL}")
    print("📋 Sincronizando slash commands...")

    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comando(s) sincronizado(s)")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")


# =============================================================================
# 1️⃣ SLASH COMMAND /ia
# =============================================================================
@bot.tree.command(name="ia", description="Faça uma pergunta para a IA")
@app_commands.describe(pergunta="Sua pergunta para a IA")
async def slash_ia(interaction: discord.Interaction, pergunta: str) -> None:
    """Slash command para interagir com a IA."""
    await interaction.response.defer(thinking=True)

    resposta = await processar_ia(pergunta)
    await enviar_resposta(interaction, resposta)


# =============================================================================
# 2️⃣ MENÇÕES (@bot) e 3️⃣ DMs
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

    # 3️⃣ DM - Mensagem direta
    if isinstance(message.channel, discord.DMChannel):
        conteudo = message.content.strip()

    # 2️⃣ Menção ao bot
    elif bot.user and bot.user.mentioned_in(message):
        # Remover menção do conteúdo
        conteudo = message.content.replace(f"<@{bot.user.id}>", "").strip()
        # Também remover menção com nickname (caso exista)
        conteudo = conteudo.replace(f"<@!{bot.user.id}>", "").strip()

    # Se tem conteúdo para processar
    if conteudo is not None:
        # Mostrar indicador de digitação
        async with message.channel.typing():
            resposta = await processar_ia(conteudo)

        await enviar_resposta(message, resposta)

    # Processar comandos de prefixo normalmente
    await bot.process_commands(message)


# =============================================================================
# Iniciar Bot
# =============================================================================
if __name__ == "__main__":
    print("🔄 Iniciando Sherlock Bot...")
    bot.run(DISCORD_TOKEN)
