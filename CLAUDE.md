# Sherlock Bot Guidance

## Table of Contents

- [Project Overview](#project-overview)
- [Development Commands](#development-commands)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Tool Roles](#tool-roles)
- [Workflows](#workflows)
- [Naming Conventions](#naming-conventions)
- [Python Guidelines](#python-guidelines)
- [Code Quality Workflow](#code-quality-workflow)
- [Testing Standards](#testing-standards)
- [Security Guidelines](#security-guidelines)
- [Development Workflow](#development-workflow)
- [Configuration Files](#configuration-files)
- [Prompt Management](#prompt-management)
- [Common Tasks](#common-tasks)
- [IDE Integration](#ide-integration)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)
- [Claude Code Settings](#claude-code-settings)

## Project Overview

**Sherlock Bot** is a Python Discord bot powered by AI via OpenRouter, built with modern Python development practices.

- **Language**: Python 3.11+
- **Package Manager**: UV (fast, modern Python package manager)
- **Code Quality**: Ruff (unified linter + formatter) + MyPy (type checker)
- **Testing**: pytest with coverage
- **Structure**: Flat (root-level files: bot.py, database.py)

## Development Commands

### Environment Management

- `uv venv` - Create virtual environment (auto-managed by UV)
- `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows) - Activate virtual environment
- `uv sync` - Install production dependencies from pyproject.toml
- `uv sync --group dev` - Install dev dependencies (ruff, mypy, pytest, pytest-cov)
- `uv pip list` - List installed packages
- `deactivate` - Deactivate virtual environment

### Package Management (via UV)

- `uv add <package>` - Add a package to dependencies
- `uv add --dev <package>` - Add a dev dependency
- `uv remove <package>` - Remove a package
- `uv lock` - Update lock file (uv.lock)
- `uv run <script>` - Run a script with UV environment
- `uv pip install <package>` - Install a package directly

> [!NOTE]
> We use `uv` for dependency management. Avoid using `pip freeze > requirements.txt` directly. Use `uv pip compile pyproject.toml -o requirements.txt` if a requirements file is needed for compatibility.

### Code Quality Commands (Ruff + MyPy)

**Ruff** unifies linting, formatting, and import sorting in a single tool:

- `ruff check .` - Run linting checks on all Python files
- `ruff check --fix .` - Fix auto-fixable issues automatically
- `ruff format .` - Format all code consistently
- `ruff format --check .` - Check formatting without changes
- `ruff check --select I .` - Check import sorting
- `ruff check --select I --fix .` - Fix import sorting

**MyPy** for static type checking:

- `mypy .` - Run type checking on all files
- `mypy bot.py database.py` - Type check specific files
- `mypy --strict .` - Run with strict mode

### Testing Commands (pytest)

- `pytest` - Run all tests in tests/ directory
- `pytest -v` - Run tests with verbose output
- `pytest --cov` - Run tests with coverage report
- `pytest --cov-report=html` - Generate HTML coverage report
- `pytest tests/test_database.py` - Run specific test file
- `pytest -k "test_name"` - Run specific test by name
- `pytest -x` - Stop on first failure

### Running the Bot

- `python bot.py` - Run bot directly
- `uv run python bot.py` - Run bot via UV environment

## Technology Stack

### Core Dependencies

- **discord.py** (≥2.3.2) - Discord bot framework
- **openai** (≥1.0.0) - OpenAI API client (used with OpenRouter)
- **python-dotenv** (≥1.0.0) - Environment variable management
- **tenacity** (≥9.1.2) - Retry logic for API calls

### Development Tools

- **Ruff** (≥0.1.0) - Fast linter, formatter, and import sorter
- **MyPy** (≥1.0.0) - Static type checker
- **pytest** (≥7.0.0) - Testing framework
- **pytest-cov** (≥4.0.0) - Coverage reporting plugin

## Project Structure

```text
sherlock_bot/
├── bot.py                    # Main Discord bot application
├── database.py               # SQLite database models and operations
├── prompt_loader.py          # System prompt loader with cache
├── pyproject.toml            # Project metadata and tool configuration
├── uv.lock                   # Dependency lock file
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore rules
├── sherlock.db               # SQLite database (auto-generated)
├── prompts/
│   └── system_prompt.md      # Sherlock system prompt (editable)
├── tests/
│   ├── __init__.py          # Package marker
│   ├── conftest.py          # pytest configuration and fixtures
│   ├── test_database.py     # Database module tests
│   ├── test_bot.py          # Bot module tests
│   └── test_prompt_loader.py # Prompt loader tests
├── docs/
│   └── ARQUITETURA.md       # Architecture and roadmap
└── .claude/                  # Claude Code configuration
    ├── settings.json        # Tool permissions and hooks
    ├── commands/            # Custom Claude Code commands
    └── agents/              # Custom agent configurations
```

### File Organization

- **bot.py** (311 lines): Discord bot with slash commands, message handling, and AI integration
- **database.py** (208 lines): SQLite database with message history and user statistics
- **tests/**: Unit tests for modules using pytest

## Tool Roles

- **UV**: Primary package and environment manager.
- **Ruff**: Unified linter and formatter. Replaces Flake8, Black, and isort.
- **MyPy**: Static type checker for Python.
- **Pytest**: Testing framework.
- **OpenRouter**: API gateway for accessing various AI models.

## Workflows

Custom workflows are available in `.claude/workflows/`:

- `/supabase-data-explorer`: Explore and analyze Supabase database data.

## Naming Conventions

- **Files/Modules**: Use snake_case (`bot.py`, `database.py`)
- **Classes**: Use PascalCase (`Message`, `ClientContext`)
- **Functions/Variables**: Use snake_case (`get_context_messages`)
- **Constants**: Use UPPER_SNAKE_CASE (`MAX_CONTEXT_MESSAGES`)
- **Private methods**: Prefix with underscore (`_internal_method`)

## Python Guidelines

### Type Hints

- Always use type hints for function parameters and return values
- Import types from `typing` module when needed
- Use `Optional` for nullable values: `Optional[str]`
- Use type hints for dataclass fields: `user_id: int`
- Document complex types in comments when needed

Example:

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class Message:
    id: int
    user_id: int
    content: str
    role: str  # "user" or "assistant"
```

### Code Style

- Follow PEP 8 style guide (enforced by Ruff)
- Limit line length to 100 characters (configured in Ruff)
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Use docstrings for modules, classes, and complex functions
- Use logging instead of print statements for bot operations

Example:

```python
import logging

logger = logging.getLogger(__name__)

def get_user_messages(user_id: int) -> list[Message]:
    """Retrieve all messages from a specific user."""
    logger.info(f"Fetching messages for user {user_id}")
    return get_context_messages(user_id)
```

### Best Practices

- Use list comprehensions for simple transformations
- Prefer `pathlib.Path` over `os.path` for file operations
- Use context managers (`with` statements) for database connections
- Handle exceptions appropriately with try/except blocks
- Use `logging` module for application logging
- Keep async/await patterns consistent (Discord bot is async)

## Code Quality Workflow

### Before Committing

1. Run linting and formatting:

   ```bash
   ruff check --fix .
   ruff format .
   ```

2. Run type checking:

   ```bash
   mypy .
   ```

3. Run tests with coverage:

   ```bash
   pytest --cov
   ```

4. Verify git status and review changes:

   ```bash
   git diff
   git status
   ```

### Automated Hooks

Claude Code hooks automatically run:

- **On file write**: Format with `ruff format`, check with `ruff check`, type check with `mypy`
- **On file edit**: Same as write
- **On stop**: Final linting pass with `ruff check`

## Testing Standards

### Test Structure

- Tests located in `tests/` directory
- Test files named `test_*.py` or `*_test.py`
- Use pytest fixtures in `conftest.py` for reusable mocks and setup
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names that explain behavior

### Test Organization

```python
class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation(self) -> None:
        """Test creating a Message instance."""
        msg = Message(id=1, user_id=123, ...)
        assert msg.id == 1

class TestDatabase:
    """Tests for database operations."""

    def test_add_message(self) -> None:
        """Test adding a message to database."""
        add_message(user_id=123, ...)
        messages = get_context_messages(123)
        assert len(messages) > 0
```

### Coverage Goals

- Aim for 80%+ test coverage
- Test database operations (CRUD)
- Test utility functions and business logic
- Use mocks for external services (Discord, OpenAI)
- Test error conditions and edge cases

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov

# Specific test file
pytest tests/test_database.py -v

# Stop on first failure
pytest -x
```

## Security Guidelines

### Environment Variables

- Use `.env` file (never commit to git)
- Use `.env.example` as template for required variables
- Required variables:
  - `DISCORD_TOKEN` - Discord bot token
  - `OPENROUTER_API_KEY` - OpenRouter API key
  - `AI_MODEL` - Model to use (e.g., `anthropic/claude-3.5-sonnet`)

### Dependencies

- Regularly check dependencies: `uv pip list`
- Keep dependencies updated but tested
- Pin versions in pyproject.toml for reproducible builds
- Use `uv lock` to track exact versions

### Code Security

- Validate user input before database operations
- Use parameterized queries (never string concatenation)
- Keep API keys in environment variables
- Use proper Discord permission scopes for bot

### Gitignore Checklist

When adding new files, ensure they are not sensitive or temporary:

- [ ] No `.env` files
- [ ] No `*.db` or `*.sqlite` files (unless specifically required)
- [ ] No `__pycache__` or `.pytest_cache`
- [ ] No `.venv` or `node_modules`

## Development Workflow

### First Time Setup

```bash
# Clone repository
git clone <repo-url>
cd sherlock_bot

# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
uv sync --group dev

# Copy environment template
cp .env.example .env
# Edit .env and add your tokens
```

### Daily Development

```bash
# Make sure venv is activated
source .venv/bin/activate

# Make code changes
# ... edit bot.py, database.py, etc ...

# Check quality before commit
ruff check --fix .
ruff format .
mypy .
pytest --cov

# Commit changes
git add .
git commit -m "Description of changes"
```

### Adding New Dependencies

```bash
# Add production dependency
uv add requests

# Add development dependency
uv add --dev pytest-asyncio

# Update lock file
uv sync
```

## Configuration Files

### pyproject.toml

Central configuration file for the project:

```toml
[project]
name = "sherlock-bot"
version = "0.1.0"
description = "Chatbot Discord com IA via OpenRouter"
requires-python = ">=3.11"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--strict-markers -v"
asyncio_mode = "auto"
```

### .env.example

```text
DISCORD_TOKEN=your_discord_token_here
OPENROUTER_API_KEY=your_openrouter_key_here
AI_MODEL=anthropic/claude-3.5-sonnet
```

## Prompt Management

### System Prompt

The Sherlock bot's system prompt (personality and instructions) is stored in `prompts/system_prompt.md` for easy maintenance and versioning.

**Location**: `prompts/system_prompt.md`

**How it Works**:
1. Prompt is loaded once at bot startup via `prompt_loader.py`
2. Uses global cache to avoid disk reads on every message
3. Falls back to default prompt if file is missing/empty
4. Supports multiline Markdown format

### Editing the Prompt

To modify the bot's behavior, simply edit `prompts/system_prompt.md`:

```markdown
# Sherlock - System Prompt

Your instructions here...

## Additional Instructions

- Guideline 1
- Guideline 2
```

> **Note**: Changes require restarting the bot (cache loads only on startup)

### Prompt Loader API

**Module**: `prompt_loader.py`

```python
from prompt_loader import load_system_prompt, clear_cache, DEFAULT_SYSTEM_PROMPT

# Load prompt (cached on first call)
prompt = load_system_prompt()

# Clear cache (useful for testing)
clear_cache()

# Access default fallback
fallback = DEFAULT_SYSTEM_PROMPT
```

### Testing Prompts

Test the prompt loader with:

```bash
pytest tests/test_prompt_loader.py -v
```

**Test Coverage**:
- ✅ File loading and parsing
- ✅ Cache functionality
- ✅ Fallback on errors
- ✅ Multiline content preservation

### Future Enhancements

The prompt management system is designed to support:
- Per-channel custom prompts (via `/persona` command)
- Prompt templates for different contexts
- Multilingual prompts
- A/B testing of prompts

## Common Tasks

### Add a New Feature

1. Create branch: `git checkout -b feature/my-feature`
2. Code the feature
3. Run quality checks: `ruff check --fix . && ruff format . && mypy .`
4. Add tests in `tests/`
5. Run tests: `pytest --cov`
6. Commit and push

### Debug the Bot

```bash
# Run with Python debugger
python -m pdb bot.py

# Or use logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Message: {content}")
```

### Database Inspection

```bash
# Open SQLite shell
sqlite3 sherlock.db

# List tables
.tables

# Show schema
.schema messages

# Query data
SELECT * FROM messages LIMIT 10;
```

## IDE Integration

### VS Code Settings

For best experience with Ruff and MyPy:

- Install Python extension (Microsoft)
- Install Ruff extension (Astral)
- Set as default formatter for Python
- Enable format on save in settings.json

### PyCharm Settings

- Set Python version to 3.11+
- Enable Ruff as external tool
- Configure MyPy as code inspection
- Run pytest directly in IDE

## Troubleshooting

### Ruff/MyPy Issues

```bash
# Clear caches
rm -rf .ruff_cache __pycache__

# Reinstall tools
uv sync --group dev --refresh
```

### Database Issues

```bash
# Backup and reset database
cp sherlock.db sherlock.db.backup
rm sherlock.db
# Bot will recreate on next run
```

### Discord Connection Issues

- Verify `DISCORD_TOKEN` is valid
- Check bot has necessary permissions in server
- Review Discord intents in bot.py
- Check API rate limiting with `tenacity` logs

## Resources

- **Discord.py**: <https://discordpy.readthedocs.io/>
- **OpenRouter API**: <https://openrouter.ai/>
- **Ruff**: <https://github.com/astral-sh/ruff>
- **MyPy**: <https://mypy.readthedocs.io/>
- **pytest**: <https://docs.pytest.org/>

## Claude Code Settings

See `.claude/settings.json` for:

- Tool permissions (allowed Bash commands)
- Automatic hooks (formatting, linting, type checking)
- Environment variables

See `.claude/commands/` for custom commands:

- `lint.md` - Code quality guidelines
- `test.md` - Testing procedures
- `architecture-review.md` - Architecture analysis
- `performance-audit.md` - Performance optimization
