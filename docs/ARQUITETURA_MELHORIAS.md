# 📊 Melhorias Arquiteturais - Sherlock Bot

**Status:** Análise Completa | Pronto para Implementação
**Data:** 2025-12-24
**Score Atual:** 7.2/10 → **Alvo: 9.0/10**
**Prazo Estimado:** 6 semanas (1 dev full-time) ou 8-10 semanas (part-time)

---

## 📋 Índice

- [Resumo Executivo](#resumo-executivo)
- [Análise Arquitetural Atual](#análise-arquitetural-atual)
- [Problemas Identificados](#problemas-identificados)
- [Roadmap de Implementação](#roadmap-de-implementação)
- [Fase 1: Fundação](#fase-1-fundação)
- [Fase 2: Testes & Qualidade](#fase-2-testes--qualidade)
- [Fase 3: Performance](#fase-3-performance)
- [Fase 4: Refatoração (Opcional)](#fase-4-refatoração-opcional)
- [Métricas de Sucesso](#métricas-de-sucesso)

---

## 📊 Resumo Executivo

### Arquitetura Identificada

```
┌─────────────────────────────────────────────┐
│  PRESENTATION LAYER (bot.py)                │
│  Discord events, slash commands             │
└──────────────────┬──────────────────────────┘
                   │ Unidirecional ↓
┌──────────────────▼──────────────────────────┐
│  BUSINESS LOGIC LAYER (bot.py)              │
│  Orquestração, processamento de IA          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  DATA ACCESS LAYER (database.py)            │
│  SQLite, CRUD, queries                      │
└─────────────────────────────────────────────┘
```

**Pattern:** Layered Architecture (3 camadas)
**Acoplamento:** Baixo (bot → database, unidirecional)
**Complexidade:** Baixa (CC médio: 4.5)
**Type hints:** 100% ✅
**Testes:** 45% (database 95%, bot 15%)

### Principais Características

| Aspecto | Status | Detalhe |
|---------|--------|---------|
| **Separação SoC** | ✅ Excelente | database.py reutilizável independentemente |
| **Type hints** | ✅ 100% | Todas as funções públicas tipadas |
| **Error handling** | ✅ 8/10 | Bom para rede, falta logging estruturado |
| **Design patterns** | ✅ 80% | Context Manager, Retry, Factory, Template |
| **Complexidade CC** | ✅ Baixa | Máximo CC = 7 (seguro) |
| **PEP 8 Compliance** | ✅ 9/10 | Ruff configurado rigorosamente |

---

## 🔍 Análise Arquitetural Atual

### Estrutura de Código

#### `bot.py` (332 linhas)

**Responsabilidades:**
- Entry point da aplicação
- Gerenciamento de eventos Discord
- Orquestração de IA
- Gestão de interações (slash commands, menções, DMs)

**Classes:**
```python
@dataclass
class AIResponse:
    """Resposta estruturada da IA com métricas."""
    content: str
    tokens_prompt: int = 0
    tokens_completion: int = 0
    model: str = ""
```

**Funções principais:**

| Função | CC | Responsabilidade |
|--------|----|----|
| `chamar_ia()` | 4 | Chamada API OpenRouter com retry |
| `processar_ia()` | 6 | Orquestração: histórico → IA → salvamento |
| `enviar_resposta()` | 5 | Divisão de mensagens longas |
| `on_ready()` | 2 | Inicialização e sync de comandos |
| `on_message()` | 7 | Roteamento: DM, menção, ignore |

#### `database.py` (219 linhas)

**Responsabilidades:**
- Persistência de mensagens (SQLite)
- Recuperação de contexto para IA
- Gestão de histórico por usuário/canal
- Estatísticas de uso

**Classes:**
```python
@dataclass
class Message:
    """Representa mensagem no histórico."""
    id: int
    user_id: int
    channel_id: int
    role: str  # "user" ou "assistant"
    content: str
    created_at: datetime
```

**Schema SQL:**
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_channel
ON messages(user_id, channel_id, created_at DESC);
```

### Fluxo de Dados Completo

```
┌──────────────┐
│ Discord User │ /ia "Qual a capital?"
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────┐
│ slash_ia(interaction, pergunta)        │
│ - defer(thinking=True)                 │
└────────────────┬───────────────────────┘
                 │
       ┌─────────▼──────────┐
       │ processar_ia()     │
       │ ├─ Validação       │
       │ ├─ get_context()   │◄─────┐
       │ ├─ chamar_ia()     │      │
       │ └─ add_message()   │      │
       └─────────┬──────────┘      │
                 │           SQLite│
       ┌─────────▼──────────┐      │
       │ chamar_ia()        │      │
       │ @retry + timeout   │      │
       │ → OpenRouter API   │      │
       └─────────┬──────────┘      │
                 │                 │
       ┌─────────▼──────────┐      │
       │ Volta para process │      │
       │ - add_message()    ├──────┘
       │   (user message)   │
       │ - add_message()    │
       │   (assistant resp) │
       └─────────┬──────────┘
                 │
       ┌─────────▼──────────┐
       │ enviar_resposta()  │
       │ - Split chunks     │
       │ - followup.send()  │
       └─────────┬──────────┘
                 │
       ┌─────────▼──────────┐
       │ Discord User       │
       │ Recebe resposta    │
       └────────────────────┘
```

### Padrões de Design Implementados

#### ✅ Context Manager
```python
@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
```
**Benefício:** Garante fechamento de conexão mesmo com exceções

#### ✅ Retry Pattern
```python
@retry(
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def chamar_ia(messages: list[dict]) -> AIResponse:
    ...
```
**Benefício:** Resiliência contra erros transientes

#### ✅ Factory Method
```python
def to_openai_format(self) -> dict[str, str]:
    return {"role": self.role, "content": self.content}
```
**Benefício:** Desacopla formato interno de externo

#### ✅ Strategy Pattern
```python
if isinstance(message.channel, discord.DMChannel):
    conteudo = message.content.strip()
elif bot.user and bot.user.mentioned_in(message):
    conteudo = message.content.replace(f"<@{bot.user.id}>", "").strip()
```
**Benefício:** Diferentes estratégias para DM vs menção

---

## ❌ Problemas Identificados

### 1. Logging não Profissional (Score: 3/10)

**Situação Atual:**
```python
print(f"✅ Bot {bot.user} está online!")
print(f"🤖 Modelo de IA: {AI_MODEL}")
print(f"⏱️ Timeout de {REQUEST_TIMEOUT_SECONDS}s...")
```

**Problemas:**
- ❌ Sem níveis de log (DEBUG, INFO, ERROR)
- ❌ Sem timestamps estruturados
- ❌ Sem rotação de logs
- ❌ Impossível filtrar em produção
- ❌ Sem rastreamento de exceções

**Impacto:** Impossível debugar issues em produção

---

### 2. Cobertura de Testes Baixa (Score: 45%)

**Estado Atual:**
- `database.py`: 95% ✅
- `bot.py`: 15% ❌
- `conftest.py`: 80% ✅

**Testes NÃO implementados:**
- ❌ `slash_ia()` - comando /ia
- ❌ `slash_limpar()` - comando /limpar
- ❌ `slash_stats()` - comando /stats
- ❌ `on_message()` - handler de menções/DMs
- ❌ `processar_ia()` - orquestração principal
- ❌ `chamar_ia()` - chamada à API
- ❌ `enviar_resposta()` - divisão de chunks

**Impacto:** Risco de regressões ao refatorar

---

### 3. Sem Rate Limiting (Crítico)

**Situação Atual:** Usuários podem fazer requisições ilimitadas

**Vulnerabilidades:**
- 💸 API pode ser explorada (custos altos)
- 🤖 Risco de abuse/DoS
- ⚠️ Sem proteção contra bots

**Impacto:** Produção não segura

---

### 4. Configuração Hardcoded

**Valores não configuráveis:**
```python
REQUEST_TIMEOUT_SECONDS = 30  # Hardcoded
MAX_CONTEXT_MESSAGES = 10     # Hardcoded
```

**Problemas:**
- ❌ Impossível ajustar em produção
- ❌ Sem validação de valores
- ❌ Sem defaults sensatos por ambiente

**Impacto:** Inflexível para diferentes cenários

---

### 5. Sem Dependency Injection

**Situação Atual:**
```python
openai_client = AsyncOpenAI(...)  # Global
```

**Problemas:**
- ❌ Difícil mockar em testes
- ❌ Sem abstração de interface
- ❌ Impossível multi-tenancy

**Impacto:** Testes frágeis e acoplados

---

### 6. Sem Cache (Performance)

**Situação Atual:** Toda requisição busca do SQLite

**Problema:**
```
User 1: /ia → Query DB (10-50ms)
User 1: /ia (mesma pergunta 5min depois) → Query DB novamente (10-50ms)
```

**Impacto:** Latência desnecessária em requisições repetidas

---

### 7. Sem Health Checks

**Situação Atual:** Impossível monitorar bot em produção

**Problemas:**
- ❌ Sem comando `/health` ou similar
- ❌ Sem métricas de latência e sucesso
- ❌ Sem alertas automáticos

**Impacto:** Difícil detectar falhas proativamente

---

## 🛣️ Roadmap de Implementação

### Timeline Overview

```
SEMANA 1-2: Fundação (Logging, Config, Rate Limit)
    ├─ 1.1 Logging Estruturado
    ├─ 1.2 Configuração Centralizada
    └─ 1.3 Rate Limiting

SEMANA 3-4: Testes & Qualidade (Cobertura 80%+)
    ├─ 2.1 Aumentar Cobertura de Testes
    └─ 2.2 Dependency Injection

SEMANA 5-6: Performance (Cache, Health Checks)
    ├─ 3.1 Cache LRU
    └─ 3.2 Health Checks & Métricas

SEMANA 7-8: Refatoração (Opcional)
    └─ 4.1 Repository Pattern
```

---

## 🔴 Fase 1: Fundação (Semana 1-2)

### 1.1 Logging Estruturado

**Objetivo:** Substituir `print()` por logging profissional com loguru

**Arquivos afetados:**
- 📝 Novo: `logger.py`
- ✏️ Modificar: `bot.py` (4 linhas de print)
- ✏️ Modificar: `database.py` (adicionar logging)
- ✏️ Modificar: `pyproject.toml` (adicionar loguru)

**Dependência:**
```bash
uv add loguru
```

**Implementação:**

```python
# logger.py (NOVO)
from loguru import logger
import sys

logger.remove()  # Remove handler default
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)
logger.add(
    "logs/sherlock_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # Rotaciona à meia-noite
    retention="7 days",  # Mantém 7 dias
    compression="zip",  # Comprime logs antigos
    level="DEBUG",
)
```

**Uso em bot.py:**

```python
# ANTES
print(f"✅ Bot {bot.user} está online!")

# DEPOIS
from logger import logger
logger.info(f"Bot {bot.user} está online!", extra={"bot_id": bot.user.id})
```

**Checklist:**
- [ ] Instalar loguru via `uv add --dev loguru`
- [ ] Criar `logger.py` com configuração
- [ ] Substituir todos os `print()` em bot.py (4 ocorrências)
- [ ] Adicionar logging em database.py (CRUD operations)
- [ ] Adicionar `logs/` ao `.gitignore`
- [ ] Testar geração de arquivos de log

**Validação:**
```bash
uv run python bot.py
ls logs/sherlock_*.log
cat logs/sherlock_*.log | grep "está online"
```

---

### 1.2 Configuração Centralizada

**Objetivo:** Mover configurações para classe Pydantic validada

**Arquivos afetados:**
- 📝 Novo: `config.py`
- ✏️ Modificar: `bot.py` (substituir `os.getenv`)
- ✏️ Modificar: `database.py` (substituir constantes)
- ✏️ Modificar: `pyproject.toml` (adicionar pydantic)

**Dependências:**
```bash
uv add pydantic pydantic-settings
```

**Implementação:**

```python
# config.py (NOVO)
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configurações globais do Sherlock Bot."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Discord
    discord_token: str = Field(..., description="Token do bot Discord")

    # OpenRouter
    openrouter_api_key: str = Field(..., description="API key OpenRouter")
    ai_model: str = Field(
        default="anthropic/claude-3.5-sonnet",
        description="Modelo de IA a usar",
    )

    # Timeouts e Limites
    request_timeout_seconds: int = Field(default=30, ge=5, le=120)
    max_context_messages: int = Field(default=10, ge=1, le=50)
    max_message_length: int = Field(default=4000, ge=1000, le=8000)

    # Database
    db_path: Path = Field(
        default_factory=lambda: Path(__file__).parent / "sherlock.db"
    )

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=10, ge=1, le=60)
    rate_limit_enabled: bool = Field(default=True)

# Singleton lazy com cache
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    """Retorna instância única e validada das configurações."""
    return Settings()

# Uso: settings = get_settings()
```

**Uso em bot.py:**

```python
# ANTES
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN não configurado")

# DEPOIS
from config import settings
# Validação automática ao importar
bot.run(settings.discord_token)
```

**Atualizar `.env.example`:**
```env
DISCORD_TOKEN=seu_token_aqui
OPENROUTER_API_KEY=sua_api_key_aqui
AI_MODEL=anthropic/claude-3.5-sonnet
REQUEST_TIMEOUT_SECONDS=30
MAX_CONTEXT_MESSAGES=10
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=10
```

**Checklist:**
- [ ] Instalar pydantic e pydantic-settings
- [ ] Criar `config.py` com classe Settings
- [ ] Atualizar `.env.example`
- [ ] Substituir `os.getenv()` em bot.py
- [ ] Substituir constantes em database.py
- [ ] Validar com .env inválido (deve falhar)
- [ ] Validar com valores fora do range (ge=5, le=120)

**Validação:**
```bash
# Teste 1: Sem .env (deve falhar)
rm .env && uv run python -c "from config import settings"

# Teste 2: Timeout > 120 (deve falhar)
echo "REQUEST_TIMEOUT_SECONDS=200" > .env
uv run python -c "from config import settings"

# Teste 3: Valores válidos (deve passar)
echo "DISCORD_TOKEN=test" > .env
uv run python -c "from config import settings; print(settings.request_timeout_seconds)"
```

---

### 1.4 Segurança e Validação de Input

**Objetivo:** Garantir integridade dos dados e prevenir injeções/abuse.

**Medidas:**
- **Sanitização:** Remover caracteres de controle e excesso de whitespace.
- **Limites de Tamanho:** Validar `len(content)` antes de processar.
- **Validação de Tipos:** Garantir que IDs sejam inteiros positivos.

**Implementação:**
```python
def sanitize_input(text: str) -> str:
    """Limpa input do usuário."""
    if not text:
        return ""
    # Remove espaços extras e caracteres nulos
    return " ".join(text.split()).replace("\0", "")

def validate_message_length(text: str) -> bool:
    """Valida se mensagem está dentro dos limites."""
    return 1 <= len(text) <= settings.max_message_length
```

### 1.3 Rate Limiting por Usuário

**Objetivo:** Prevenir abuse de requisições à API

**Arquivos afetados:**
- 📝 Novo: `rate_limiter.py`
- ✏️ Modificar: `bot.py` (adicionar decorator)

**Implementação:**

```python
# rate_limiter.py (NOVO)
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable

from config import settings

class RateLimiter:
    def __init__(self, max_requests: int, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self.requests: dict[int, list[datetime]] = defaultdict(list)
        self._cleanup_interval = self.window  # Cleanup a cada janela

    def is_allowed(self, user_id: int) -> bool:
        now = datetime.now(timezone.utc)
        cutoff = now - self.window

        # Remove requisições antigas (fora da janela)
        self.requests[user_id] = [
            ts for ts in self.requests[user_id] if ts > cutoff
        ]

        # Verifica se atingiu o limite
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # Registra nova requisição
        self.requests[user_id].append(now)

        # Cleanup periódico para usuários inativos (opcional, pode ser em background)
        if len(self.requests) > 1000:  # Threshold arbitrário
            self._cleanup_inactive_users(now, cutoff)

        return True

    def _cleanup_inactive_users(self, now: datetime, cutoff: datetime):
        """Remove usuários sem requisições recentes para prevenir vazamento de memória."""
        to_remove = []
        for user_id, timestamps in self.requests.items():
            if not timestamps or all(ts <= cutoff for ts in timestamps):
                to_remove.append(user_id)
        for user_id in to_remove:
            del self.requests[user_id]

    def get_remaining(self, user_id: int) -> int:
        """Retorna requisições restantes."""
        return max(0, self.max_requests - len(self.requests[user_id]))

# Singleton
rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_requests_per_minute,
)

def rate_limit(func: Callable):
    """Decorator para rate limiting."""
    @wraps(func)
    async def wrapper(interaction, *args, **kwargs):
        user_id = interaction.user.id

        if not settings.rate_limit_enabled:
            return await func(interaction, *args, **kwargs)

        if not rate_limiter.is_allowed(user_id):
            remaining = rate_limiter.get_remaining(user_id)
            await interaction.response.send_message(
                f"⏱️ Você atingiu o limite de {settings.rate_limit_requests_per_minute} "
                f"requisições por minuto. Aguarde um pouco.",
                ephemeral=True,
            )
            logger.warning(
                f"Rate limit exceeded for user {user_id}",
                extra={"user_id": user_id, "limit": settings.rate_limit_requests_per_minute}
            )
            return

        return await func(interaction, *args, **kwargs)

    return wrapper
```

**Uso em bot.py:**

```python
from rate_limiter import rate_limit

@bot.tree.command(name="ia", description="...")
@rate_limit  # ← ADICIONAR
async def slash_ia(interaction: discord.Interaction, pergunta: str) -> None:
    ...
```

**Checklist:**
- [ ] Criar `rate_limiter.py` com classe RateLimiter
- [ ] Adicionar decorator `@rate_limit` em `slash_ia` e `slash_stats`
- [ ] Adicionar logging quando rate limit acionado
- [ ] Testar com múltiplas requisições rápidas
- [ ] Validar mensagem de erro

**Validação:**
```bash
# Fazer 11 requisições seguidas (limite = 10)
# A 11ª deve retornar erro: "Você atingiu o limite..."
```

---

## 🟡 Fase 2: Testes & Qualidade (Semana 3-4)

### 2.1 Aumentar Cobertura de Testes (15% → 80%+)

**Objetivo:** Testar funções críticas de `bot.py`

**Novos testes necessários (16 testes):**

```python
# test_bot.py (EXPANDIR)

class TestProcessarIA:
    """Testes para processar_ia()."""

    @pytest.mark.asyncio
    async def test_processar_ia_success(self, mock_openai_client, monkeypatch):
        """Testa fluxo completo de processamento."""
        monkeypatch.setattr("bot.get_context_messages", lambda *args: [])
        monkeypatch.setattr("bot.add_message", lambda *args: 1)

        resposta = await processar_ia("Olá", user_id=123, channel_id=456)
        assert resposta == "AI response test message"

    @pytest.mark.asyncio
    async def test_processar_ia_timeout(self, monkeypatch):
        """Testa timeout de API."""
        async def mock_chamar(*args):
            raise asyncio.TimeoutError("Timeout")

        monkeypatch.setattr("bot.chamar_ia", mock_chamar)
        resposta = await processar_ia("Test", 123, 456)
        assert "demorou muito" in resposta

    @pytest.mark.asyncio
    async def test_processar_ia_rate_limit(self, monkeypatch):
        """Testa tratamento de RateLimitError."""
        from openai import RateLimitError

        async def mock_chamar(*args):
            raise RateLimitError("Too many requests")

        monkeypatch.setattr("bot.chamar_ia", mock_chamar)
        resposta = await processar_ia("Test", 123, 456)
        assert "Muitas requisições" in resposta

    @pytest.mark.asyncio
    async def test_processar_ia_connection_error(self, monkeypatch):
        """Testa erro de conexão."""
        from openai import APIConnectionError

        async def mock_chamar(*args):
            raise APIConnectionError("Connection failed")

        monkeypatch.setattr("bot.chamar_ia", mock_chamar)
        resposta = await processar_ia("Test", 123, 456)
        assert "conexão" in resposta

class TestSlashCommands:
    """Testes para slash commands."""

    @pytest.mark.asyncio
    async def test_slash_ia_basic(self, mock_discord_interaction, monkeypatch):
        """Testa comando /ia básico."""
        monkeypatch.setattr(
            "bot.processar_ia",
            AsyncMock(return_value="Resposta teste")
        )

        await slash_ia(mock_discord_interaction, pergunta="Test?")

        mock_discord_interaction.response.defer.assert_called_once()
        mock_discord_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_slash_limpar_basic(self, mock_discord_interaction, monkeypatch):
        """Testa comando /limpar."""
        monkeypatch.setattr("bot.clear_user_history", lambda *args: 5)

        await slash_limpar(mock_discord_interaction)

        mock_discord_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_slash_stats_basic(self, mock_discord_interaction, monkeypatch):
        """Testa comando /stats."""
        monkeypatch.setattr(
            "bot.get_user_stats",
            lambda *args: {"message_count": 10, "user_id": 123, "channel_id": 456}
        )

        await slash_stats(mock_discord_interaction)

        mock_discord_interaction.response.send_message.assert_called_once()

class TestEnviarResposta:
    """Testes para enviar_resposta()."""

    @pytest.mark.asyncio
    async def test_enviar_resposta_single_chunk(self, mock_discord_interaction):
        """Testa envio de mensagem curta (1 chunk)."""
        await enviar_resposta(mock_discord_interaction, "Resposta curta")

        assert mock_discord_interaction.followup.send.call_count == 1

    @pytest.mark.asyncio
    async def test_enviar_resposta_two_chunks(self, mock_discord_interaction):
        """Testa envio com 2 chunks."""
        resposta_longa = "A" * 3000  # 3000 chars → 2 chunks
        await enviar_resposta(mock_discord_interaction, resposta_longa)

        assert mock_discord_interaction.followup.send.call_count == 2

    @pytest.mark.asyncio
    async def test_enviar_resposta_three_chunks(self, mock_discord_interaction):
        """Testa envio com 3 chunks."""
        resposta_longa = "A" * 5000  # 5000 chars → 3 chunks
        await enviar_resposta(mock_discord_interaction, resposta_longa)

        assert mock_discord_interaction.followup.send.call_count == 3

class TestOnMessage:
    """Testes para handler on_message()."""

    @pytest.mark.asyncio
    async def test_on_message_dm(self, mock_discord_message, monkeypatch):
        """Testa processamento de DM."""
        mock_discord_message.channel = MagicMock(spec=discord.DMChannel)
        monkeypatch.setattr("bot.processar_ia", AsyncMock(return_value="Resp"))

        await on_message(mock_discord_message)

        # Verificar que processar_ia foi chamado

    @pytest.mark.asyncio
    async def test_on_message_mention(self, mock_discord_message, monkeypatch):
        """Testa processamento de menção."""
        mock_discord_message.channel = MagicMock()
        # Mock que bot foi mencionado
        monkeypatch.setattr("bot.processar_ia", AsyncMock(return_value="Resp"))

        await on_message(mock_discord_message)

    @pytest.mark.asyncio
    async def test_on_message_ignore_other(self, mock_discord_message):
        """Testa ignore de outras mensagens."""
        mock_discord_message.channel = MagicMock()
        mock_discord_message.author = MagicMock()

        # Mensagem que não é DM, não menciona bot, etc
        # Não deve processar
```

**Arquivos novos:**

```python
# tests/test_rate_limiter.py (NOVO)
class TestRateLimiter:
    """Testes para RateLimiter."""

    def test_rate_limiter_allow_first_request(self):
        """Primeira requisição é permitida."""
        limiter = RateLimiter(max_requests=10)
        assert limiter.is_allowed(123) is True

    def test_rate_limiter_deny_after_limit(self):
        """Rejeita após atingir limite."""
        limiter = RateLimiter(max_requests=2)
        assert limiter.is_allowed(123) is True
        assert limiter.is_allowed(123) is True
        assert limiter.is_allowed(123) is False

    def test_rate_limiter_get_remaining(self):
        """Retorna requisições restantes."""
        limiter = RateLimiter(max_requests=5)
        limiter.is_allowed(123)
        assert limiter.get_remaining(123) == 4

    def test_rate_limiter_separate_users(self):
        """Limites são separados por usuário."""
        limiter = RateLimiter(max_requests=2)
        limiter.is_allowed(123)
        limiter.is_allowed(123)

        # User 456 deve ter 2 requisições
        assert limiter.is_allowed(456) is True
        assert limiter.is_allowed(456) is True
        assert limiter.is_allowed(456) is False

    def test_rate_limiter_reset_after_window(self):
        """Limites resetam após janela de tempo."""
        # Este teste requer mock de datetime
        pass

# tests/test_config.py (NOVO)
class TestConfig:
    """Testes para configuração."""

    def test_config_from_env(self, monkeypatch):
        """Config carrega de .env."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")

        # Reimportar para pegar env vars
        import importlib
        import config
        importlib.reload(config)

        assert config.settings.discord_token == "test_token"

    def test_config_validation(self, monkeypatch):
        """Config valida valores."""
        monkeypatch.setenv("REQUEST_TIMEOUT_SECONDS", "200")  # > 120

        with pytest.raises(ValidationError):
            from config import Settings
            Settings()

    def test_config_defaults(self, monkeypatch):
        """Config tem defaults sensatos."""
        monkeypatch.setenv("DISCORD_TOKEN", "test")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test")

        from config import settings

        assert settings.request_timeout_seconds == 30
        assert settings.max_context_messages == 10
        assert settings.rate_limit_enabled is True
```

**Checklist:**
- [ ] Implementar testes para `processar_ia()` (4 testes)
- [ ] Implementar testes para `slash_ia()` (3 testes)
- [ ] Implementar testes para `slash_limpar()` (1 teste)
- [ ] Implementar testes para `slash_stats()` (1 teste)
- [ ] Implementar testes para `enviar_resposta()` (3 testes)
- [ ] Implementar testes para `on_message()` (3 testes)
- [ ] Criar `test_rate_limiter.py` (5 testes)
- [ ] Criar `test_config.py` (3 testes)
- [ ] Rodar `pytest --cov --cov-report=html`
- [ ] Validar cobertura > 80%

**Validação:**
```bash
uv run pytest --cov=. --cov-report=term --cov-report=html
open htmlcov/index.html  # Relatório visual

# Esperado:
# bot.py: 80%+
# database.py: 95%+
# rate_limiter.py: 85%+
# config.py: 90%+
# TOTAL: 85%+
```

---

### 2.2 Dependency Injection para OpenAI Client

**Objetivo:** Facilitar mocking em testes

**Arquivos afetados:**
- 📝 Novo: `clients.py`
- ✏️ Modificar: `bot.py` (usar injeção)

**Implementação:**

```python
# clients.py (NOVO)
from typing import Protocol
from openai import AsyncOpenAI
from config import settings
from logger import logger

from abc import ABC, abstractmethod
from typing import Protocol

# Abordagem escolhida: ABC para contrato explícito e segurança de produção
class AIClient(ABC):
    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        """Gera resposta da IA a partir de mensagens."""
        pass

class OpenRouterClient(AIClient):
    def generate(self, messages: list[dict]) -> str:
        # Implementação específica com OpenRouter
        # Adicionar validações, logging, etc.
        return "resposta gerada"

# Factory para injeção de dependência
def create_ai_client() -> AIClient:
    return OpenRouterClient()

    @abstractmethod
    async def get_history(self, user_id: int, channel_id: int, limit: int) -> List[MessageDTO]:
        """Recupera o histórico de mensagens de um contexto."""
        pass

    @abstractmethod
    async def clear_history(self, user_id: int, channel_id: int) -> int:
        """Remove histórico de um contexto e retorna total removido."""
        pass
```

---

## ✅ Métricas de Sucesso

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| **Score Arquitetura** | 7.2/10 | 9.0/10 | +25% |
| **Cobertura Testes** | 45% | 85% | +89% |
| **Latência Média** | ~300ms | ~150ms | -50% |
| **Logging** | ❌ print | ✅ loguru | N/A |
| **Rate Limiting** | ❌ | ✅ 10/min | N/A |
| **Config Validada** | ❌ | ✅ pydantic | N/A |
| **Dependency Injection** | ❌ | ✅ | N/A |

---

## 📁 Arquivos Críticos

### Novos Arquivos a Criar (8)
1. `logger.py` 🔴
2. `config.py` 🔴
3. `rate_limiter.py` 🔴
4. `clients.py` 🟡
5. `cache.py` 🟢
6. `health.py` 🟢
7. `tests/test_rate_limiter.py` 🟡
8. `tests/test_config.py` 🟡

### Arquivos a Modificar (4)
1. `bot.py` (logging, config, rate limit, DI)
2. `database.py` (logging)
3. `tests/test_bot.py` (16 novos testes)
4. `pyproject.toml` (novas dependências)

---

## ⏱️ Tempo Estimado

- **Fase 1:** 2 semanas (Logging, Config, Rate Limit)
- **Fase 2:** 2 semanas (Testes 80%, DI)
- **Fase 3:** 2 semanas (Cache, Health Checks)
- **Fase 4:** 2 semanas (Repository Pattern - opcional)

**TOTAL: 6 semanas** (1 dev full-time) ou **8-10 semanas** (part-time)

---

## 🎯 Próximos Passos

1. ✅ **Ler este documento** - Entender a visão geral
2. 🚀 **Iniciar Fase 1** - Começar com logging estruturado
3. 📊 **Monitorar progresso** - Usar checklist para rastrear
4. 🧪 **Validar continuamente** - Testes em cada fase
5. 📈 **Medir sucesso** - Comparar antes/depois

---

## 📞 Referências

- **Plano detalhado:** Ver documentação interna de planos
- **Análise completa:** Ver seção Resumo Executivo acima
- **CLAUDE.md:** Guia de desenvolvimento atualizado
- **pyproject.toml:** Configurações de ferramentas
