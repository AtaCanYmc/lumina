# Contributing to Lumina

Thank you for contributing to Lumina. This document outlines the development workflow, code standards, and pull request verification requirements.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Quality and Style](#code-quality-and-style)
- [Project Architecture](#project-architecture)
- [Commit Message Specification](#commit-message-specification)
- [Pull Request Checklist](#pull-request-checklist)

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/AtaCanYmc/lumina.git
   cd lumina
   ```
3. Set upstream remote:
   ```bash
   git remote add upstream https://github.com/AtaCanYmc/lumina.git
   ```

## Development Setup

Install development dependencies and the editable package:

```bash
make dev
```

Alternatively, configure manually:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
pip install pytest ruff black isort pre-commit
```

Install the Git pre-commit hooks:

```bash
pre-commit install
```

## Code Quality and Style

### Formatting and Linting

All code must pass formatting and static analysis checks:

```bash
make lint
# Or individually:
# isort --check-only .
# black --check .
# ruff check .
```

To automatically format files:

```bash
make format
# Or individually:
# isort .
# black .
# ruff check --fix .
```

### Running Tests

Execute the full test suite before committing:

```bash
make test
# Or directly: pytest
```

All 50 test assertions must pass without regressions.

## Project Architecture

```text
lumina/
├── assets/
│   └── images/readme/         # Documentation render assets (logo, sample lithophanes)
├── docs/                      # Technical documentation
│   ├── API.md
│   ├── CLI.md
│   └── CONTRIBUTING.md
├── src/lumina/
│   ├── __init__.py            # Public package exports
│   ├── cli.py                 # Click CLI commands and entry points
│   ├── core/
│   │   ├── image_service.py   # Resizing, contrast enhancement, spiral algorithms
│   │   ├── shapes.py          # Boundary masking strategies (rect, circle, heart)
│   │   ├── stl_service.py     # Heightmap meshing and STL generation
│   │   └── viewer.py          # 3D WebGL viewport and physical light simulation
│   ├── gui/                   # PySide6 desktop GUI application
│   │   ├── app.py             # Main window and dark theme stylesheet
│   │   ├── main.py            # GUI entry point launcher
│   │   └── widgets/           # Dropzone, LithophaneTab, SpiralTab
│   ├── templates/
│   │   └── viewer.html        # Standalone Three.js 3D viewer template
│   └── utils/
│       └── common_utils.py    # Shared geometry and array utilities
├── tests/                     # Pytest test suite
├── LICENSE                    # MIT license
├── Makefile                   # Build and development task automation
├── pyproject.toml             # Package specification and tool configuration
├── README.md                  # Project overview and quick start
├── ROADMAP.md                 # Project milestones and feature pipeline
└── SECURITY.md                # Vulnerability disclosure policy
```

## Commit Message Specification

Lumina enforces the [Conventional Commits](https://www.conventionalcommits.org/) standard. Commit messages must follow the format:

```text
<type>(<scope>): <subject>
```

### Allowed Types

| Type | Description |
| :--- | :--- |
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting, missing semi-colons, no code logic change |
| `refactor` | Code restructuring without changing external behavior |
| `perf` | Code change improving execution performance |
| `test` | Adding missing tests or correcting existing tests |
| `build` | Changes to build system or package manifests |
| `ci` | Changes to CI configuration files and scripts |
| `chore` | Routine repository maintenance |

### Examples

- `feat(shapes): add star-shaped lithophane border strategy`
- `fix(cli): handle non-zero frame border offset calculations`
- `docs(readme): add technical FAQ and slicer print recommendations`

## Pull Request Checklist

Before submitting your pull request, verify:

1. A dedicated feature branch was created (`git checkout -b feat/your-feature`).
2. All unit tests pass locally (`pytest`).
3. Code formatting conforms to repository style (`isort --check-only .`, `black --check .`, `ruff check .`).
4. Commit history follows Conventional Commits.
5. New functionality is covered by unit tests in `tests/`.
6. Relevant documentation in `docs/` or `README.md` is updated.
