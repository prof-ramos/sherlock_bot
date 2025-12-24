# Code Quality and Linting

Run Python code quality checks using Ruff (linting + formatting) and MyPy (type checking).

## Purpose

This command helps you maintain code quality using modern, fast Python tools:
- **Ruff**: Fast, unified linter + formatter + import sorter (replaces black, isort, flake8)
- **MyPy**: Static type checker for Python

> [!NOTE]
> Claude Code hooks are configured to be **non-blocking**. Linting and type checking issues will be reported but will not prevent file writes.

## Usage

```
/lint
```

## What this command does

1. **Linting with Ruff** - Checks for style and correctness issues
2. **Formatting with Ruff** - Auto-fixes formatting and imports
3. **Type checking with MyPy** - Validates type hints
4. **Provides detailed feedback** on all code quality issues

## Example Commands

### Ruff (Unified Linting + Formatting + Import Sorting)

Ruff combines the functionality of black, isort, and flake8 into a single, fast tool.

#### Linting
```bash
# Check all Python files for issues
ruff check .

# Fix all auto-fixable issues
ruff check --fix .

# Check with specific rule (e.g., imports)
ruff check --select I .
```

#### Formatting
```bash
# Format all Python files
ruff format .

# Check formatting without changes
ruff format --check .

# Format specific file
ruff format bot.py
```

#### Import Sorting
```bash
# Check import sorting
ruff check --select I .

# Fix imports
ruff check --select I --fix .
```

#### Combined Workflow
```bash
# Fix all issues and format
ruff check --fix .
ruff format .

# Or in one go with both checks
ruff check --fix . && ruff format .
```

### MyPy (Type Checking)

Type checking catches errors before runtime by verifying type hints.

```bash
# Check types in all files
mypy .

# Check specific module
mypy bot.py database.py

# Check with strict mode
mypy --strict .

# Show detailed error information
mypy --show-error-codes .
```

## Configuration Files

### pyproject.toml

The project uses centralized configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--strict-markers -v"
asyncio_mode = "auto"
```

## Best Practices

- **Before committing**: Run `ruff check --fix . && ruff format . && mypy .`
- **Use type hints**: Always add type hints to functions and classes
- **Fix issues promptly**: Address linting errors as soon as they appear
- **Understand warnings**: Read MyPy output to understand type issues
- **Consistent formatting**: Ruff ensures uniform code style across the project
- **Use the hooks**: Claude Code automatically runs Ruff and MyPy on file changes

## Rule Selection in Ruff

The project uses specific Ruff rules:

- **E**: PyCodeStyle errors (style issues)
- **F**: Pyflakes (logical errors)
- **W**: PyCodeStyle warnings
- **I**: isort (import sorting)
- **N**: pep8-naming (naming conventions)
- **UP**: pyupgrade (Python syntax modernization)
- **B**: flake8-bugbear (common bugs)
- **C4**: flake8-comprehensions (list/dict comprehension optimization)

Excluded:
- **E501**: Line too long (already controlled by line-length setting)

## Common Issues and Fixes

### Import Order Issues
```bash
# Fix automatically
ruff check --select I --fix .
```

### Line Too Long
```bash
# Already handled by Ruff formatter with line-length=100
ruff format .
```

### Unused Imports
```bash
# Remove unused imports automatically
ruff check --fix .
```

### Type Errors
```bash
# Identify type issues
mypy .

# Add type hints to fix
def function(x: int) -> str:  # Specify parameter and return types
    return str(x)
```

## Running in CI/CD

### Pre-commit Checks
```bash
# Before committing to git
ruff check --fix .
ruff format .
mypy .
pytest --cov
```

### Automated Hooks in Claude Code

Claude Code automatically runs:
- **Ruff formatting** on every file edit
- **Ruff linting** on every file write
- **MyPy type checking** on every file change
- **Pytest** when code is saved (if tests exist)

No manual action needed - quality checks happen automatically!

## Why Ruff?

Ruff combines three tools into one:

| Traditional | Modern |
|-------------|--------|
| black → format code | Ruff format |
| isort → sort imports | Ruff check --select I |
| flake8 → lint code | Ruff check |

Benefits:
- ✅ **10-100x faster** than traditional tools
- ✅ **Single tool** to learn and configure
- ✅ **Built-in compatibility** with black and isort
- ✅ **Active development** and community support

## Resources

- **Ruff Documentation**: https://docs.astral.sh/ruff/
- **MyPy Documentation**: https://mypy.readthedocs.io/
- **PEP 8 Style Guide**: https://pep8.org/
- **Type Hints Guide**: https://docs.python.org/3/library/typing.html
