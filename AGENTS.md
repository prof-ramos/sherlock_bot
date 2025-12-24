# Agent Guidelines - Sherlock Bot

**Python 3.11+** | UV package manager | Discord bot with OpenRouter AI

## Commands
- Install: `uv sync --group dev`
- Lint/Format: `ruff check --fix . && ruff format .`
- Type Check: `mypy .`
- All Tests: `pytest --cov`
- Single Test: `pytest tests/test_file.py::TestClass::test_name -v`
- Run Bot: `uv run python bot.py`

## Code Style
- **Imports**: Standard library → third-party → local; group with blank lines
- **Formatting**: PEP 8, 100 char line length, enforced by Ruff
- **Types**: Always type hints (params/returns), use `Optional[str]`, all dataclass fields (public and private) must have explicit type hints; use Optional[T] for defaults of None and annotate default_factory fields with their return type
- **Naming**: snake_case (files/functions), PascalCase (classes), UPPER_SNAKE_CASE (constants), `_private` methods
- **Error Handling**: Try/except with specific exceptions, use `logger.exception()` for errors
- **Logging**: Use `logger` module (loguru), not `print`; log levels: debug/info/warning/error/critical
- **Async**: Use async functions for all Discord event handlers and command handlers; await asynchronous calls instead of chaining .then/.catch; avoid mixing callback-style and promise-style code; use top-level async initialization for bot startup; wrap awaited operations in try/catch with proper error logging
- **File Paths**: Prefer `pathlib.Path` over `os.path`
- **Docstrings**: Modules, classes, complex functions required
- **Testing**: pytest, fixtures in conftest.py, AAA pattern, 80%+ coverage target
