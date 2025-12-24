# 🕵️ Sherlock Bot

Chatbot Discord com IA via OpenRouter. Responde em 3 cenários:
- **Slash command**: `/ia [pergunta]`
- **Menções**: `@Sherlock [pergunta]`
- **DMs**: Envie uma mensagem direta para o bot

## 🚀 Setup Rápido

### 1. Pré-requisitos

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) (gerenciador de pacotes)

### 2. Instalação

```bash
# Clonar e entrar no diretório
cd sherlock_bot

# Instalar dependências com UV
uv sync

# Copiar e configurar variáveis de ambiente
cp .env.example .env
```

### 3. Configurar Credenciais

Edite o arquivo `.env`:

```env
DISCORD_TOKEN=seu_token_discord
OPENROUTER_API_KEY=sua_chave_openrouter
```

#### Como obter as credenciais:

**Discord Token:**
1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma aplicação ou selecione existente
3. Vá em "Bot" no menu lateral
4. Clique em "Reset Token" e copie o token

**⚠️ IMPORTANTE:** Habilite os intents privilegiados:
1. No portal, vá em "Bot" > "Privileged Gateway Intents"
2. Ative **MESSAGE CONTENT INTENT**
3. Ative **DIRECT MESSAGES INTENT** (se disponível separadamente)

**OpenRouter API Key:**
1. Acesse [OpenRouter.ai](https://openrouter.ai/)
2. Crie uma conta e adicione créditos
3. Vá em "Keys" e crie uma nova chave

### 4. Executar

```bash
# Ativar venv e rodar
uv run python bot.py
```

## 📝 Comandos

| Comando | Descrição |
|---------|-----------|
| `/ia [pergunta]` | Pergunte algo para a IA |
| `@Bot [pergunta]` | Mencione o bot em qualquer canal |
| DM | Envie mensagem direta para o bot |

## 🔧 Estrutura do Projeto

```
sherlock_bot/
├── bot.py           # Código principal do bot
├── pyproject.toml   # Configuração do projeto
├── .env.example     # Exemplo de variáveis de ambiente
├── .env             # Variáveis de ambiente (não versionado)
└── README.md        # Este arquivo
```

## 🎯 Modelo de IA

Por padrão, usa `anthropic/claude-3.5-sonnet`. Para mudar, edite no `.env`:

```env
AI_MODEL=openai/gpt-4-turbo-preview
```

Veja modelos disponíveis em [OpenRouter Models](https://openrouter.ai/models).

## 📜 Licença

MIT License
