#!/bin/bash
# Script para iniciar o Sherlock Bot
# Uso: ./start.sh [--background]

set -e  # Sair em caso de erro

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PID_FILE=".bot.pid"

echo -e "${BLUE}🤖 Iniciando Sherlock Bot...${NC}"

# Verificar se .env existe
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo "Execute './install.sh' primeiro para configurar o ambiente"
    exit 1
fi

# Verificar se bot já está rodando
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Bot já está rodando (PID: $PID)${NC}"
        echo "Use './stop.sh' para desligar o bot primeiro"
        exit 1
    else
        # PID file existe mas processo não está rodando
        echo -e "${YELLOW}⚠️  Removendo PID file obsoleto${NC}"
        rm "$PID_FILE"
    fi
fi

# Verificar se dependências estão instaladas
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado.${NC}"
    echo "Execute './install.sh' primeiro"
    exit 1
fi

# Rodar em background ou foreground
if [[ "$1" == "--background" ]] || [[ "$1" == "-b" ]]; then
    echo -e "${GREEN}🚀 Iniciando bot em background...${NC}"
    nohup uv run python bot.py > logs/bot.out 2>&1 &
    BOT_PID=$!
    echo "$BOT_PID" > "$PID_FILE"
    echo -e "${GREEN}✅ Bot iniciado! (PID: $BOT_PID)${NC}"
    echo ""
    echo "Logs: tail -f logs/bot.out"
    echo "Parar: ./stop.sh"
else
    echo -e "${GREEN}🚀 Iniciando bot em foreground...${NC}"
    echo -e "${YELLOW}💡 Use Ctrl+C para parar ou './start.sh --background' para rodar em background${NC}"
    echo ""

    # Salvar PID temporariamente
    echo $$ > "$PID_FILE"

    # Trap para limpar PID file ao sair
    trap "rm -f $PID_FILE; echo -e '\n${YELLOW}🛑 Bot encerrado${NC}'" EXIT INT TERM

    # Rodar bot
    uv run python bot.py
fi
