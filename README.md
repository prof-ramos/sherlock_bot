# 🕵️ Sherlock Bot

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Quality](https://img.shields.io/badge/code%20quality-ruff%20%2B%20mypy-green.svg)](https://github.com/astral-sh/ruff)

> 🤖 Chatbot Discord inteligente com IA integrada via OpenRouter. Responde a perguntas, mantém contexto de conversas e oferece uma experiência natural de chat.

## ✨ Funcionalidades

- **💬 Interação Natural**: Responde via slash commands, menções e mensagens diretas
- **🧠 IA Avançada**: Integração com múltiplos modelos via OpenRouter (Claude, GPT-4, etc.)
- **📚 Histórico de Conversas**: Mantém contexto entre mensagens no mesmo canal/DM
- **⚡ Rate Limiting**: Protege contra abuso com limites configuráveis
- **🔒 Segurança**: Validação robusta de tokens e configurações
- **📊 Estatísticas**: Comando para ver uso pessoal
- **🗑️ Limpeza**: Comando para limpar histórico de conversas
- **🎯 Suporte Multi-idioma**: Respostas em português brasileiro por padrão

## 🛠️ Tecnologias Utilizadas

- **🐍 Python 3.11+**: Linguagem principal
- **🤖 discord.py 2.3.2+**: Framework Discord
- **🧠 OpenRouter**: Gateway para modelos de IA
- **📦 UV**: Gerenciamento rápido de dependências
- **🗄️ SQLite**: Banco de dados local para histórico
- **🔧 Pydantic**: Validação e configurações
- **⚡ Tenacity**: Retry automático para APIs
- **📝 Loguru**: Logging estruturado
- **🧪 pytest**: Testes com cobertura
- **🎨 Ruff**: Linting e formatação unificada
- **🔍 MyPy**: Verificação de tipos

## 📋 Pré-requisitos

- **Python 3.11 ou superior**
- **UV** (instalador moderno de pacotes Python)
- **Conta Discord** com permissões para criar bot
- **Conta OpenRouter** com créditos para API

## 🚀 Instalação

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/prof-ramos/sherlock_bot.git
cd sherlock_bot
```

### Passo 2: Instalar Dependências

```bash
# Instalar todas as dependências (produção + desenvolvimento)
uv sync --group dev

# Verificar instalação
uv run python --version
```

### Passo 3: Configurar Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais (ver seção abaixo)
nano .env  # ou seu editor preferido
```

## ⚙️ Configuração

### Credenciais Obrigatórias

Edite o arquivo `.env` com suas credenciais:

```env
# Token do bot Discord (obrigatório, mínimo 50 caracteres)
DISCORD_TOKEN=seu_token_discord_aqui

# Chave da API OpenRouter (obrigatório, mínimo 50 caracteres)
OPENROUTER_API_KEY=sua_chave_openrouter_aqui
```

### Configurações Opcionais

```env
# Modelo de IA (padrão: anthropic/claude-3.5-sonnet)
AI_MODEL=anthropic/claude-3.5-sonnet

# Timeout para chamadas da IA em segundos (5-120)
REQUEST_TIMEOUT_SECONDS=30

# Máximo de mensagens de contexto por conversa
MAX_CONTEXT_MESSAGES=10

# Comprimento máximo de resposta em caracteres
MAX_MESSAGE_LENGTH=4000

# Habilitar rate limiting
RATE_LIMIT_ENABLED=true

# Máximo de requisições por minuto por usuário
RATE_LIMIT_REQUESTS_PER_MINUTE=10

# Nível de logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 🔑 Como Obter as Credenciais

#### Discord Bot Token

1. **Acesse o Portal**: [Discord Developer Portal](https://discord.com/developers/applications)
2. **Crie uma Aplicação**: Clique em "New Application" e dê um nome
3. **Configure o Bot**:
   - Vá em "Bot" no menu lateral
   - Clique em "Reset Token" e copie o token gerado
   - Em "Privileged Gateway Intents", ative:
     - ✅ **MESSAGE CONTENT INTENT**
     - ✅ **SERVER MEMBERS INTENT** (opcional)
4. **Convide o Bot**: Em "OAuth2 > URL Generator", selecione "bot" e gere URL para convidar

#### OpenRouter API Key

1. **Acesse**: [OpenRouter.ai](https://openrouter.ai/)
2. **Crie Conta**: Registre-se gratuitamente
3. **Adicione Créditos**: Deposite fundos via cartão ou crypto
4. **Gere Chave**: Vá em "Keys" > "Create Key"
5. **Copie**: Use a chave gerada no `.env`

### 🐛 Troubleshooting de Configuração

- **Erro "Intents not enabled"**: Verifique se ativou MESSAGE CONTENT INTENT
- **Erro "Invalid token"**: Confirme que copiou o token correto do Discord
- **Erro "API key invalid"**: Verifique créditos no OpenRouter
- **Timeout errors**: Aumente `REQUEST_TIMEOUT_SECONDS`

## ▶️ Executando o Bot

### Modo Desenvolvimento

```bash
# Executar diretamente
uv run python bot.py

# Ou com logging detalhado
LOG_LEVEL=DEBUG uv run python bot.py
```

### Modo Produção (Recomendado)

Use um process manager como PM2, systemd ou Docker:

```bash
# Com PM2
npm install -g pm2
pm2 start "uv run python bot.py" --name sherlock-bot

# Verificar status
pm2 status
pm2 logs sherlock-bot
```

### 🛑 Parando o Bot

```bash
# Ctrl+C no terminal ou
pkill -f "python bot.py"
```

## 💬 Uso e Comandos

### Comandos Disponíveis

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `/ia [pergunta]` | Pergunte algo para a IA | `/ia O que é Python?` |
| `/limpar` | Limpa histórico da conversa no canal atual | `/limpar` |
| `/stats` | Mostra estatísticas de uso pessoal | `/stats` |
| `@Bot [pergunta]` | Mencione o bot em qualquer canal | `@Sherlock O que é IA?` |
| **DM** | Envie mensagem direta para o bot | `Olá, me ajude com Python` |

### Exemplos de Uso

```
Usuário: /ia Como fazer um loop em Python?
Bot: Para fazer um loop em Python, você pode usar for ou while...

Usuário: @Sherlock Explique recursão
Bot: Recursão é quando uma função chama a si mesma...

Usuário (DM): Qual a diferença entre lista e tupla?
Bot: Listas são mutáveis, tuplas são imutáveis...
```

### ⚙️ Configurações Avançadas

- **Rate Limiting**: Protege contra spam (configurável em `.env`)
- **Contexto**: Mantém histórico de até 10 mensagens por conversa
- **Timeout**: 30s padrão para respostas da IA
- **Limite de Tamanho**: Respostas truncadas em 4000 caracteres

### 🎭 Customizando o Comportamento do Bot

O prompt do sistema (personalidade e instruções) do bot está em `prompts/system_prompt.md` e pode ser facilmente editado:

```markdown
# Sherlock - System Prompt

Você é Sherlock, um assistente inteligente e prestativo.

Responda de forma clara, concisa e amigável em português brasileiro.
```

**Editar prompt**:
```bash
nano prompts/system_prompt.md  # ou seu editor preferido
```

**Aplicar mudanças**: Reinicie o bot após editar o prompt.

Para mais detalhes, consulte a seção [Prompt Management](CLAUDE.md#prompt-management) em `CLAUDE.md`.

## 🧪 Testes

### Executar Todos os Testes

```bash
# Com cobertura
uv run pytest --cov --cov-report=html

# Apenas testes unitários
uv run pytest tests/

# Teste específico
uv run pytest tests/test_bot.py -v
```

### Verificar Qualidade do Código

```bash
# Linting e formatação
uv run ruff check . --fix
uv run ruff format .

# Verificação de tipos
uv run mypy .
```

## 📁 Estrutura do Projeto

```
sherlock_bot/
├── bot.py                    # 🏠 Código principal do bot Discord
├── config.py                 # ⚙️ Configurações validadas com Pydantic
├── database.py               # 🗄️ SQLite com histórico de conversas
├── logger.py                 # 📝 Logging estruturado com Loguru
├── rate_limiter.py           # 🛡️ Controle de rate limiting
├── prompt_loader.py          # 🎭 Carregador de prompts do sistema
├── pyproject.toml            # 📦 Configuração do projeto e dependências
├── uv.lock                   # 🔒 Lock file das dependências
├── .env.example              # 📋 Template de variáveis de ambiente
├── .env                      # 🔐 Credenciais (não versionado)
├── .gitignore                # 🚫 Arquivos ignorados pelo Git
├── prompts/                  # 🎭 Prompts do sistema (personalizáveis)
│   └── system_prompt.md      # 📝 System prompt do Sherlock
├── tests/                    # 🧪 Testes automatizados
│   ├── conftest.py           # 🏗️ Configurações compartilhadas
│   ├── test_*.py             # 🧪 Testes por módulo
│   └── __init__.py           # 📦 Pacote de testes
├── docs/                     # 📚 Documentação
│   ├── ARQUITETURA.md        # 🏛️ Arquitetura e design
│   └── ARQUITETURA_MELHORIAS.md # 🚀 Roadmap e melhorias
├── .claude/                  # 🤖 Configurações do Claude Code
│   ├── agents/               # 👥 Agentes especializados
│   ├── commands/             # 🛠️ Comandos customizados
│   └── settings.json         # ⚙️ Configurações de hooks
└── README.md                 # 📖 Este arquivo
```

## 🤖 Modelos de IA Suportados

O bot suporta qualquer modelo disponível no OpenRouter. Padrão: `anthropic/claude-3.5-sonnet`.

### Modelos Recomendados

| Modelo | Descrição | Uso Ideal |
|--------|-----------|-----------|
| `anthropic/claude-3.5-sonnet` | **Padrão** - Equilibrado, inteligente | Geral |
| `openai/gpt-4-turbo-preview` | Muito inteligente, mais lento | Tarefas complexas |
| `anthropic/claude-3-haiku` | Rápido e eficiente | Respostas simples |
| `meta-llama/llama-3-70b-instruct` | Open-source, gratuito | Testes |

### Alterar Modelo

```env
AI_MODEL=openai/gpt-4-turbo-preview
```

**Nota**: Modelos pagos requerem créditos no OpenRouter. Veja [modelos disponíveis](https://openrouter.ai/models).

## 🚀 Deploy e Produção

### Com Docker (Recomendado)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync --no-dev
CMD ["uv", "run", "python", "bot.py"]
```

```bash
# Build e run
docker build -t sherlock-bot .
docker run --env-file .env sherlock-bot
```

### Com Railway/Vercel

1. Conecte o repositório Git
2. Configure variáveis de ambiente
3. Deploy automático

### Monitoramento

```bash
# Logs em tempo real
uv run python bot.py 2>&1 | tee bot.log

# Verificar saúde
curl http://localhost:8080/health  # Se usar FastAPI health check
```

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:

### 1. Fork e Clone

```bash
git clone https://github.com/seu-username/sherlock_bot.git
cd sherlock_bot
```

### 2. Crie uma Branch

```bash
git checkout -b feature/nova-funcionalidade
```

### 3. Desenvolva

```bash
# Instalar dependências de dev
uv sync --group dev

# Rodar testes antes de commitar
uv run pytest --cov

# Verificar qualidade
uv run ruff check . --fix && uv run mypy .
```

### 4. Commit e Push

```bash
git add .
git commit -m "feat: adicionar nova funcionalidade"
git push origin feature/nova-funcionalidade
```

### 5. Pull Request

Abra um PR no GitHub com descrição detalhada.

### 📋 Guidelines

- ✅ Siga PEP 8 e use type hints
- ✅ Adicione testes para novas funcionalidades
- ✅ Mantenha cobertura >80%
- ✅ Documente mudanças significativas
- ✅ Use commits convencionais (`feat:`, `fix:`, `docs:`)

## 🐛 Problemas e Suporte

### Issues Comuns

- **Bot não responde**: Verifique intents no Discord Developer Portal
- **Erro de API**: Confirme créditos no OpenRouter
- **Rate limit**: Aguarde ou aumente limite em `.env`
- **Timeout**: Aumente `REQUEST_TIMEOUT_SECONDS`

### Obtendo Ajuda

- 🐛 **Bugs**: [Abra uma issue](https://github.com/prof-ramos/sherlock_bot/issues)
- 💡 **Ideias**: [Discussions](https://github.com/prof-ramos/sherlock_bot/discussions)
- 📧 **Contato**: Via Discord ou email

## 📈 Roadmap

- [ ] 🖼️ Suporte a imagens/vision
- [ ] 🎵 Integração com Spotify/YouTube
- [ ] 🌐 Suporte a webhooks externos
- [ ] 📊 Dashboard de analytics
- [ ] 🔄 Modo conversacional avançado
- [ ] 🌍 Suporte multi-idioma

## 📜 Licença

Este projeto está sob a licença **MIT**. Veja [LICENSE](LICENSE) para detalhes.

---

<div align="center">

**Feito com ❤️ para a comunidade Discord**

[⭐ Star no GitHub](https://github.com/prof-ramos/sherlock_bot) • [📖 Documentação Completa](docs/) • [🐛 Reportar Bug](https://github.com/prof-ramos/sherlock_bot/issues)

</div>
