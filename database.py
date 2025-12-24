"""
Módulo de banco de dados SQLite para histórico de conversas.

Armazena mensagens por usuário/canal com contexto para IA.
"""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from config import settings
from logger import logger


@dataclass
class Message:
    """Representa uma mensagem no histórico."""

    id: int
    user_id: int
    channel_id: int
    role: str  # "user" ou "assistant"
    content: str
    created_at: datetime

    def to_openai_format(self) -> dict[str, str]:
        """Converte para formato da API OpenAI."""
        return {"role": self.role, "content": self.content}


def parse_datetime(dt_str: str) -> datetime:
    """
    Converte string de data do banco para objeto datetime de forma robusta.

    Tenta múltiplos formatos comuns do SQLite.
    """
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",  # ISO com microsegundos
        "%Y-%m-%d %H:%M:%S",  # ISO sem microsegundos
        "%Y-%m-%dT%H:%M:%S.%f",  # ISO T com microsegundos
        "%Y-%m-%dT%H:%M:%S",  # ISO T sem microsegundos
    ]

    # Tenta fromisoformat primeiro (mais rápido em Python 3.11+)
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        pass

    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue

    logger.error(f"Falha ao parsear data: {dt_str}. Formatos tentados: {formats}")
    raise ValueError(f"Não foi possível parsear a data: {dt_str}")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager para conexão com o banco."""
    conn = None
    try:
        conn = sqlite3.connect(str(settings.db_path))
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except sqlite3.DatabaseError as e:
        if conn:
            conn.rollback()
        logger.error(
            "Erro ao acessar banco de dados",
            extra={"error": str(e), "db_path": str(settings.db_path)},
        )
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception(
            "Erro inesperado na conexão com banco de dados",
            extra={"error": str(e)},
        )
        raise
    finally:
        if conn:
            conn.close()


def init_db() -> None:
    """Inicializa o banco de dados criando as tabelas necessárias."""
    logger.info(
        "Inicializando banco de dados",
        extra={"db_path": str(settings.db_path)},
    )
    try:
        with get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Índice para busca rápida por usuário/canal
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_channel
                ON messages(user_id, channel_id, created_at DESC)
            """)
            # Commit é feito automaticamente pelo context manager
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(
            "Erro ao inicializar banco de dados",
            extra={"error": str(e)},
        )
        raise


def add_message(user_id: int, channel_id: int, role: str, content: str) -> int:
    """
    Adiciona uma mensagem ao histórico.

    Args:
        user_id: ID do usuário Discord
        channel_id: ID do canal (ou DM)
        role: "user" ou "assistant"
        content: Conteúdo da mensagem

    Returns:
        ID da mensagem inserida

    Raises:
        ValueError: Se o role for inválido
        RuntimeError: Se a inserção falhar
    """
    if role not in ("user", "assistant"):
        raise ValueError(f"Role inválido: {role}. Deve ser 'user' ou 'assistant'.")

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (user_id, channel_id, role, content)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, channel_id, role, content),
            )
            # Commit é feito automaticamente pelo context manager

            if cursor.lastrowid is None:
                raise RuntimeError("Falha ao inserir mensagem: lastrowid é None")

            logger.debug(
                "Mensagem inserida",
                extra={
                    "message_id": cursor.lastrowid,
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "role": role,
                    "content_length": len(content),
                },
            )

            return cursor.lastrowid
    except Exception as e:
        logger.error(
            "Erro ao inserir mensagem",
            extra={
                "user_id": user_id,
                "channel_id": channel_id,
                "role": role,
                "error": str(e),
            },
        )
        raise


def get_conversation_history(
    user_id: int,
    channel_id: int,
    limit: int | None = None,
) -> list[Message]:
    """
    Recupera o histórico de conversas de um usuário em um canal.

    Args:
        user_id: ID do usuário Discord
        channel_id: ID do canal
        limit: Número máximo de mensagens (usa settings.max_context_messages se None)

    Returns:
        Lista de mensagens ordenadas da mais antiga para a mais recente
    """
    if limit is None:
        limit = settings.max_context_messages

    try:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, user_id, channel_id, role, content, created_at
                FROM messages
                WHERE user_id = ? AND channel_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (user_id, channel_id, limit),
            ).fetchall()

        # Converter para objetos Message e inverter ordem (mais antiga primeiro)
        messages = []
        for row in reversed(rows):
            created_at = parse_datetime(row["created_at"])

            messages.append(
                Message(
                    id=row["id"],
                    user_id=row["user_id"],
                    channel_id=row["channel_id"],
                    role=row["role"],
                    content=row["content"],
                    created_at=created_at,
                )
            )

        logger.debug(
            "Histórico recuperado",
            extra={
                "user_id": user_id,
                "channel_id": channel_id,
                "messages_count": len(messages),
            },
        )

        return messages
    except Exception as e:
        logger.error(
            "Erro ao recuperar histórico",
            extra={
                "user_id": user_id,
                "channel_id": channel_id,
                "error": str(e),
            },
        )
        raise


def get_context_messages(user_id: int, channel_id: int) -> list[dict[str, str]]:
    """
    Retorna mensagens formatadas para API OpenAI.

    Args:
        user_id: ID do usuário Discord
        channel_id: ID do canal

    Returns:
        Lista de dicts no formato {"role": "...", "content": "..."}
    """
    history = get_conversation_history(user_id, channel_id)
    return [msg.to_openai_format() for msg in history]


def clear_user_history(user_id: int, channel_id: int | None = None) -> int:
    """
    Limpa o histórico de um usuário.

    Args:
        user_id: ID do usuário Discord
        channel_id: Se None, limpa todos os canais

    Returns:
        Número de mensagens removidas
    """
    try:
        with get_connection() as conn:
            if channel_id is not None:
                cursor = conn.execute(
                    "DELETE FROM messages WHERE user_id = ? AND channel_id = ?",
                    (user_id, channel_id),
                )
            else:
                cursor = conn.execute(
                    "DELETE FROM messages WHERE user_id = ?",
                    (user_id,),
                )
            # Commit é feito automaticamente pelo context manager no sucesso
            rowcount = cursor.rowcount

        logger.info(
            "Histórico limpo",
            extra={
                "user_id": user_id,
                "channel_id": channel_id,
                "messages_removed": rowcount,
            },
        )

        return rowcount
    except Exception as e:
        logger.error(
            "Erro ao limpar histórico",
            extra={
                "user_id": user_id,
                "channel_id": channel_id,
                "error": str(e),
            },
        )
        raise


def get_user_stats(user_id: int) -> dict[str, int]:
    """
    Retorna estatísticas do usuário.

    Args:
        user_id: ID do usuário Discord

    Returns:
        Dict com total_messages e total_channels
    """
    try:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT channel_id) as total_channels
                FROM messages
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        stats = {
            "total_messages": row["total_messages"],
            "total_channels": row["total_channels"],
        }

        logger.debug(
            "Estatísticas recuperadas",
            extra={
                "user_id": user_id,
                "total_messages": stats["total_messages"],
                "total_channels": stats["total_channels"],
            },
        )

        return stats
    except Exception as e:
        logger.error(
            "Erro ao recuperar estatísticas",
            extra={"user_id": user_id, "error": str(e)},
        )
        raise


# Removida inicialização automática no import para evitar efeitos colaterais.
# Chame database.init_db() explicitamente no ponto de entrada da aplicação.
