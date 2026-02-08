# Contributing to Telegram News Bot

Thank you for your interest in contributing! This document provides guidelines for development.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/news-bot.git
cd news-bot
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt
```

### 4. Setup Pre-commit Hooks

```bash
pre-commit install
```

### 5. Configure Environment

```bash
copy .env.example .env
# Edit .env with your credentials
```

### 6. Run Tests

```bash
pytest -v
```

## Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

Run before committing:

```bash
# Format code
black bot/ tests/

# Lint
ruff check bot/ tests/

# Type check
mypy bot/
```

Or let pre-commit handle it:

```bash
pre-commit run --all-files
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=bot --cov-report=html
```

### Run Specific Tests

```bash
pytest tests/test_filters.py -v
pytest tests/test_storage.py::TestStorage::test_daily_post_count -v
```

## Project Structure

```
news-bot/
├── bot/                    # Main application code
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── client.py          # Bot client
│   ├── config.py          # Configuration
│   ├── storage.py         # Database layer
│   ├── filters.py         # Message filtering
│   ├── processors.py      # Message processing
│   ├── ai_service.py      # AI integration
│   ├── rate_limiter.py    # Rate limiting
│   ├── monitoring.py      # Monitoring/metrics
│   ├── health.py          # Health checks
│   └── utils.py           # Utilities
├── tests/                 # Test suite
│   ├── conftest.py        # Test fixtures
│   ├── test_filters.py
│   ├── test_storage.py
│   └── test_processors.py
├── .github/
│   └── workflows/
│       └── ci.yml         # CI/CD pipeline
├── requirements.txt       # Production deps
├── requirements-dev.txt   # Dev deps
├── pyproject.toml        # Project config
└── README.md
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write code
- Add tests
- Update documentation

### 3. Test Your Changes

```bash
pytest
```

### 4. Commit

```bash
git add .
git commit -m "feat: add new feature"
```

Commit message format:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` tests
- `refactor:` code refactoring
- `chore:` maintenance

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**: Explain what and why
- **Tests**: Add tests for new features
- **Documentation**: Update docs if needed
- **CI**: Ensure all checks pass

## Code Review Process

1. Automated checks run (tests, linting, type checking)
2. Maintainer reviews code
3. Address feedback
4. Merge when approved

## Reporting Issues

Use GitHub Issues with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Logs if applicable

## Questions?

Open a GitHub Discussion or issue!

---

Thank you for contributing! 🚀
