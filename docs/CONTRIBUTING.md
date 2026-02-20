# Contributing to Lumina

Thank you for your interest in contributing to Lumina! 🎉

## Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/AtaCanYmc/lumina.git
   cd lumina
   ```
3. **Install** in development mode:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   pip install pytest ruff
   ```

## Development Workflow

### Running Tests

```bash
pytest
```

All tests must pass before submitting a PR.

### Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting:

```bash
ruff check .
ruff check --fix .  # Auto-fix issues
```

### Project Structure

```
lumina/
├── src/lumina/
│   ├── __init__.py          # Main API functions
│   ├── cli.py                # CLI commands
│   └── core/
│       ├── image_service.py  # Image processing
│       ├── stl_service.py    # STL generation
│       └── shapes.py         # Shape strategies
├── tests/                    # Unit tests
└── docs/                     # Documentation
```

## Submitting Changes

1. Create a **feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and **commit**:
   ```bash
   git commit -m "Add: your feature description"
   ```

3. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a **Pull Request** on GitHub

## Commit Message Guidelines

- `Add:` New feature
- `Fix:` Bug fix
- `Docs:` Documentation changes
- `Refactor:` Code refactoring
- `Test:` Adding or updating tests

## Questions?

Open an issue or reach out to the maintainers.

Thank you for contributing! 🚀
