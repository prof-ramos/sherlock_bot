# Scripts de Gerenciamento do Sherlock Bot

Este documento descreve os scripts de linha de comando disponíveis para facilitar o desenvolvimento e operação do Sherlock Bot.

## 📋 Índice

- [install.sh](#installsh) - Instalação de dependências
- [start.sh](#startsh) - Iniciar o bot
- [stop.sh](#stopsh) - Parar o bot
- [test.sh](#testsh) - Rodar testes
- [lint.sh](#lintsh) - Verificar qualidade de código

---

## 🔧 install.sh

Instala as dependências do projeto usando UV.

### Uso

```bash
./install.sh [--dev]

```bash

### Opções

- **Sem argumentos**: Instala apenas dependências de produção
- **--dev**: Instala também dependências de desenvolvimento (ruff, mypy, pytest, etc.)

### O que faz

1. ✅ Verifica se UV está instalado
2. ✅ Cria arquivo `.env` a partir de `.env.example` (se não existir)
3. ✅ Instala dependências via `uv sync`
4. ✅ Cria diretório `logs/`

### Exemplos

```bash
# Instalação para produção
./install.sh

# Instalação para desenvolvimento
./install.sh --dev

```bash

### Primeira vez?

```bash
# 1. Instalar dependências
./install.sh --dev

# 2. Configurar variáveis de ambiente
nano .env  # Adicione DISCORD_TOKEN, OPENROUTER_API_KEY, etc.

# 3. Rodar testes
./test.sh

# 4. Iniciar bot
./start.sh

```

---

## 🚀 start.sh

Inicia o Sherlock Bot.

### Uso

```bash
./start.sh [--background]

```bash

### Opções

- **Sem argumentos**: Roda em foreground (Ctrl+C para parar)
- **--background** ou **-b**: Roda em background (daemon)

### O que faz

1. ✅ Verifica se `.env` existe
2. ✅ Verifica se bot já está rodando
3. ✅ Inicia o bot (foreground ou background)
4. ✅ Salva PID em `.bot.pid` (modo background)

### Exemplos

```bash
# Rodar em foreground (logs no terminal)
./start.sh

# Rodar em background (daemon)
./start.sh --background

# Ver logs do bot em background
tail -f logs/bot.out
tail -f logs/sherlock_*.log

```bash

### Troubleshooting

**Erro: "Arquivo .env não encontrado"**

```bash
./install.sh  # Cria .env a partir de .env.example
nano .env     # Configure suas chaves

```

**Erro: "Bot já está rodando"**

```bash
./stop.sh     # Para o bot atual
./start.sh    # Inicia novamente

```

---

## 🛑 stop.sh

Para o Sherlock Bot que está rodando em background.

### Uso

```bash
./stop.sh

```bash

### O que faz

1. ✅ Lê PID do arquivo `.bot.pid`
2. ✅ Envia SIGTERM (graceful shutdown)
3. ✅ Aguarda até 10 segundos
4. ✅ Se necessário, força encerramento com SIGKILL
5. ✅ Remove arquivo `.bot.pid`

### Exemplos

```bash
# Parar bot em background
./stop.sh

# Verificar se bot ainda está rodando
ps aux | grep bot.py

```bash

### Notas

- Se o bot estiver rodando em **foreground**, use **Ctrl+C** ao invés deste script
- O script tenta graceful shutdown primeiro (SIGTERM) antes de forçar (SIGKILL)

---

## 🧪 test.sh

Executa os testes do projeto usando pytest.

### Uso

```bash
./test.sh [opções do pytest]

```bash

### Opções

- **Sem argumentos**: Roda todos os testes com coverage
- **Argumentos pytest**: Passados diretamente para pytest

### O que faz

1. ✅ Verifica se pytest está instalado
2. ✅ Executa testes com ou sem coverage
3. ✅ Mostra relatório de cobertura

### Exemplos

```bash
# Rodar todos os testes com coverage
./test.sh

# Rodar com verbose
./test.sh -v

# Rodar teste específico
./test.sh -k test_database

# Rodar arquivo específico
./test.sh tests/test_bot.py

# Gerar relatório HTML de coverage
./test.sh --cov-report=html
# Abrir: htmlcov/index.html

# Parar no primeiro erro
./test.sh -x

# Rodar em paralelo (mais rápido)
./test.sh -n auto  # Requer pytest-xdist

```bash

### Comandos úteis

```bash
# Ver apenas testes que falharam
./test.sh --lf

# Ver testes mais lentos
./test.sh --durations=10

# Rodar com output detalhado
./test.sh -vv -s

```

---

## 🔍 lint.sh

Executa verificações de qualidade de código (linting, formatação, type checking).

### Uso

```bash
./lint.sh [--fix]

```bash

### Opções

- **Sem argumentos**: Apenas verifica (não modifica arquivos)
- **--fix**: Corrige problemas automaticamente quando possível

### O que faz

1. ✅ **Ruff Check**: Linting (PEP 8, imports, etc.)
2. ✅ **Ruff Format**: Formatação de código
3. ✅ **MyPy**: Type checking

### Exemplos

```bash
# Apenas verificar (não modifica)
./lint.sh

# Verificar e corrigir automaticamente
./lint.sh --fix

```bash

### Integração com Git

```bash
# Antes de commit
./lint.sh --fix
git add .
git commit -m "feat: nova funcionalidade"

# Se lint falhar, corrija os problemas
./lint.sh --fix

```bash

### Verificações individuais

```bash
# Apenas ruff check
ruff check .

# Apenas formatação
ruff format .

# Apenas type checking
uv run mypy .

```

---

## 🔄 Workflow Típico de Desenvolvimento

### Primeira configuração

```bash
# 1. Clonar repositório
git clone <repo-url>
cd sherlock_bot

# 2. Instalar dependências de dev
./install.sh --dev

# 3. Configurar .env
cp .env.example .env
nano .env  # Adicionar tokens

# 4. Rodar testes
./test.sh

# 5. Iniciar bot
./start.sh

```bash

### Desenvolvimento diário

```bash
# 1. Atualizar dependências (se necessário)
./install.sh --dev

# 2. Fazer alterações no código
# ... editar bot.py, database.py, etc ...

# 3. Verificar qualidade
./lint.sh --fix

# 4. Rodar testes
./test.sh

# 5. Testar bot localmente
./start.sh

# 6. Commit
git add .
git commit -m "feat: descrição"
git push

```bash

### Antes de criar Pull Request

```bash
# Verificar tudo está OK
./lint.sh --fix       # Corrigir código
./test.sh             # Rodar testes
git status            # Verificar arquivos
git diff              # Revisar mudanças

```

---

## 🐛 Troubleshooting

### UV não encontrado

```bash
# Instalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Adicionar ao PATH (se necessário)
export PATH="$HOME/.cargo/bin:$PATH"

```bash

### Dependências não instaladas

```bash
# Reinstalar tudo
rm -rf .venv
./install.sh --dev

```bash

### Bot não inicia

```bash
# Verificar logs
cat logs/bot.out
tail -f logs/sherlock_*.log

# Verificar .env
cat .env  # Verificar se tokens estão configurados

# Rodar em foreground para ver erros
./start.sh  # (sem --background)

```bash

### Testes falhando

```bash
# Rodar com verbose para ver detalhes
./test.sh -vv

# Rodar teste específico que está falhando
./test.sh -k test_nome_especifico -vv

# Verificar coverage
./test.sh --cov-report=html
open htmlcov/index.html

```bash

### Lint falhando

```bash
# Ver detalhes dos erros
ruff check .

# Corrigir automaticamente
./lint.sh --fix

# Se persistir, verificar cada ferramenta
ruff check --diff .
ruff format --diff .
uv run mypy .

```

---

## 📁 Arquivos Gerados

Os scripts criam/usam os seguintes arquivos:

| Arquivo | Descrição | Gitignore? |

|---------|-----------|------------|

| `.bot.pid` | PID do processo do bot (background) | ✅ Sim |

| `logs/bot.out` | Output do bot em background | ✅ Sim |

| `logs/sherlock_*.log` | Logs diários do bot | ✅ Sim |

| `.coverage` | Dados de cobertura de testes | ✅ Sim |

| `htmlcov/` | Relatório HTML de coverage | ✅ Sim |

| `.pytest_cache/` | Cache do pytest | ✅ Sim |

| `.venv/` | Ambiente virtual Python | ✅ Sim |

| `sherlock.db` | Banco de dados SQLite | ✅ Sim |

---

## 🔗 Referências

- **UV**: https://github.com/astral-sh/uv
- **Ruff**: https://github.com/astral-sh/ruff
- **MyPy**: https://mypy.readthedocs.io/
- **pytest**: https://docs.pytest.org/
- **Discord.py**: https://discordpy.readthedocs.io/

---

## 💡 Dicas

### Aliases úteis (adicione ao ~/.bashrc ou ~/.zshrc)

```bash
alias bot-start='./start.sh --background'
alias bot-stop='./stop.sh'
alias bot-restart='./stop.sh && ./start.sh --background'
alias bot-logs='tail -f logs/bot.out'
alias bot-test='./test.sh'
alias bot-lint='./lint.sh --fix'

```bash

### Monitoramento do bot

```bash
# Ver logs em tempo real
tail -f logs/bot.out

# Ver logs estruturados
tail -f logs/sherlock_$(date +%Y-%m-%d).log

# Verificar se bot está rodando
ps aux | grep bot.py

# Verificar uso de memória
ps aux | grep bot.py | awk '{print $4"%"}'

```bash

### CI/CD

Os scripts podem ser usados em pipelines de CI/CD:

```yaml
# .github/workflows/test.yml
- name: Install dependencies
  run: ./install.sh --dev

- name: Run linting
  run: ./lint.sh

- name: Run tests
  run: ./test.sh

```

---

**Última atualização**: 2025-12-27
