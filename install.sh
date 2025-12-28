#!/bin/bash
# Script de instalação de dependências do Sherlock Bot
# Uso: ./install.sh [--dev]

set -e  # Sair em caso de erro

echo "🔧 Instalando dependências do Sherlock Bot..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se UV está instalado
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ UV não encontrado.${NC}"
    echo "Instale UV primeiro: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}✓${NC} UV encontrado: $(uv --version)"

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado.${NC}"
    if [ -f .env.example ]; then
        echo "Copiando .env.example para .env..."
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Configure suas chaves em .env antes de rodar o bot!${NC}"
    else
        echo -e "${RED}❌ .env.example não encontrado!${NC}"
        exit 1
    fi
fi

# Instalar dependências
if [[ "$1" == "--dev" ]]; then
    echo "📦 Instalando dependências de desenvolvimento..."
    uv sync --group dev
    echo -e "${GREEN}✅ Dependências de desenvolvimento instaladas!${NC}"
else
    echo "📦 Instalando dependências de produção..."
    uv sync
    echo -e "${GREEN}✅ Dependências instaladas!${NC}"
    echo -e "${YELLOW}💡 Use './install.sh --dev' para instalar dependências de desenvolvimento${NC}"
fi

# Criar diretório de logs
mkdir -p logs

# Inicializar banco de dados (será criado automaticamente no primeiro run)
echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo ""
echo "Próximos passos:"
echo "1. Configure suas chaves em .env"
echo "2. Execute './start.sh' para iniciar o bot"
echo "3. Execute './test.sh' para rodar os testes"
