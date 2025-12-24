"""
Logging configurado com loguru para o Sherlock Bot.

Fornece logging estruturado, centralizado e rotacionado automaticamente.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger as _logger

# Remove o handler padrão do loguru
_logger.remove()

# Criar diretório de logs de forma robusta
logs_dir: Optional[Path] = None
try:
    logs_dir = Path(__file__).parent.resolve() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
except Exception as e:
    # Se falhar ao criar diretório de logs, usa tempfile como fallback
    import tempfile

    try:
        logs_dir = Path(tempfile.mkdtemp(prefix="sherlock_logs_"))
        logs_dir.mkdir(parents=True, exist_ok=True)
    except Exception as fallback_e:
        # Se até tempfile falhar, desabilita logging para arquivo
        logs_dir = None
        print(
            f"ERRO: Não foi possível criar diretório de logs: {e}, fallback também falhou: {fallback_e}",
            file=sys.stderr,
        )

# Handler para stderr (console)
_logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)

# Handler para arquivo com rotação (só se logs_dir for válido)
if logs_dir is not None:
    _logger.add(
        logs_dir / "sherlock_{time:YYYY-MM-DD}.log",
        format=("{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"),
        level="DEBUG",
        rotation="00:00",  # Rotaciona à meia-noite
        retention="7 days",  # Mantém 7 dias
        compression="zip",  # Comprime logs antigos
    )

# Exportar logger para uso em outros módulos
logger = _logger
