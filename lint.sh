#!/bin/bash
# Script para rodar verificações de qualidade de código
# Uso: ./lint.sh [--fix]

set -e  # Sair em caso de erro

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Verificando qualidade do código...${NC}"
echo ""

FIX_MODE=false
if [[ "$1" == "--fix" ]]; then
    FIX_MODE=true
    echo -e "${YELLOW}🔧 Modo de correção automática ativado${NC}"
    echo ""
fi

# Contador de erros
ERRORS=0

# 1. Ruff Linting
echo -e "${BLUE}1️⃣  Ruff Linting${NC}"
if [ "$FIX_MODE" = true ]; then
    if ruff check --fix .; then
        echo -e "${GREEN}✅ Ruff check passou (com correções)${NC}"
    else
        echo -e "${RED}❌ Ruff check falhou${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    if ruff check .; then
        echo -e "${GREEN}✅ Ruff check passou${NC}"
    else
        echo -e "${RED}❌ Ruff check falhou${NC}"
        echo -e "${YELLOW}💡 Use './lint.sh --fix' para corrigir automaticamente${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

# 2. Ruff Formatting
echo -e "${BLUE}2️⃣  Ruff Formatting${NC}"
if [ "$FIX_MODE" = true ]; then
    if ruff format .; then
        echo -e "${GREEN}✅ Código formatado${NC}"
    else
        echo -e "${RED}❌ Formatação falhou${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    if ruff format --check .; then
        echo -e "${GREEN}✅ Formatação correta${NC}"
    else
        echo -e "${RED}❌ Código precisa ser formatado${NC}"
        echo -e "${YELLOW}💡 Use './lint.sh --fix' para formatar automaticamente${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

# 3. MyPy Type Checking
echo -e "${BLUE}3️⃣  MyPy Type Checking${NC}"
if uv run mypy .; then
    echo -e "${GREEN}✅ Type checking passou${NC}"
else
    echo -e "${RED}❌ Type checking falhou${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Resumo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Todas as verificações passaram!${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS verificação(ões) falharam${NC}"
    if [ "$FIX_MODE" = false ]; then
        echo -e "${YELLOW}💡 Use './lint.sh --fix' para corrigir automaticamente${NC}"
    fi
    exit 1
fi
