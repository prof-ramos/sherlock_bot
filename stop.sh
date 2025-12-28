#!/bin/bash
# Script para parar o Sherlock Bot
# Uso: ./stop.sh

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PID_FILE=".bot.pid"

echo -e "${YELLOW}🛑 Parando Sherlock Bot...${NC}"

# Verificar se PID file existe
if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}❌ Bot não está rodando (PID file não encontrado)${NC}"

    # Tentar encontrar processo python bot.py
    BOT_PID=$(pgrep -f "python.*bot.py" || true)
    if [ -n "$BOT_PID" ]; then
        echo -e "${YELLOW}⚠️  Encontrei processo bot.py rodando (PID: $BOT_PID)${NC}"
        echo "Deseja encerrar este processo? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            kill "$BOT_PID"
            echo -e "${GREEN}✅ Processo $BOT_PID encerrado${NC}"
        fi
    fi
    exit 1
fi

# Ler PID do arquivo
PID=$(cat "$PID_FILE")

# Verificar se processo está rodando
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Processo $PID não está rodando${NC}"
    rm "$PID_FILE"
    echo -e "${GREEN}✅ PID file removido${NC}"
    exit 0
fi

# Tentar graceful shutdown (SIGTERM)
echo -e "${YELLOW}📤 Enviando SIGTERM para PID $PID...${NC}"
kill "$PID"

# Aguardar até 10 segundos para o processo encerrar
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Bot encerrado com sucesso!${NC}"
        rm "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Se ainda estiver rodando, forçar (SIGKILL)
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Processo não respondeu ao SIGTERM, forçando encerramento...${NC}"
    kill -9 "$PID"
    sleep 1

    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${RED}❌ Falha ao encerrar processo $PID${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Bot encerrado (forçado)${NC}"
        rm "$PID_FILE"
    fi
fi
