#!/bin/bash
# Script para rodar testes do Sherlock Bot
# Uso: ./test.sh [opções do pytest]

set -e  # Sair em caso de erro

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Rodando testes do Sherlock Bot...${NC}"
echo ""

# Verificar se dependências de dev estão instaladas
if ! uv run pytest --version &> /dev/null; then
    echo -e "${RED}❌ pytest não encontrado.${NC}"
    echo "Execute './install.sh --dev' para instalar dependências de desenvolvimento"
    exit 1
fi

# Se nenhum argumento for passado, roda com coverage
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}📊 Rodando testes com cobertura...${NC}"
    uv run pytest --cov --cov-report=term-missing

    echo ""
    echo -e "${GREEN}✅ Testes concluídos!${NC}"
    echo ""
    echo -e "${YELLOW}💡 Dicas:${NC}"
    echo "  ./test.sh -v                    # Testes verbose"
    echo "  ./test.sh -k test_name          # Rodar teste específico"
    echo "  ./test.sh tests/test_bot.py     # Rodar arquivo específico"
    echo "  ./test.sh --cov-report=html     # Gerar relatório HTML"
else
    # Passar argumentos diretamente para pytest
    echo -e "${YELLOW}📊 Rodando: pytest $@${NC}"
    uv run pytest "$@"
fi

echo ""
echo -e "${GREEN}✅ Testes finalizados!${NC}"
