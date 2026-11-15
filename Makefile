.PHONY: help install dev test lint format clean build _ensure_pip macos-app macos-dmg

PYTHON ?= $(shell which python3 2>/dev/null || which python 2>/dev/null || echo python3)
PIP ?= $(PYTHON) -m pip

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  install    Install package and production dependencies"
	@echo "  dev        Install development dependencies and editable package"
	@echo "  test       Run unit tests with pytest"
	@echo "  lint       Run static analysis and style checks (isort, black, ruff)"
	@echo "  format     Auto-format codebase (isort, black, ruff)"
	@echo "  clean      Remove build artifacts, caches, and bytecode"
	@echo "  build      Build source distribution and wheel"

_ensure_pip:
	@$(PYTHON) -m pip --version >/dev/null 2>&1 || $(PYTHON) -m ensurepip --upgrade >/dev/null 2>&1 || true

install: _ensure_pip
	$(PIP) install -r requirements.txt
	$(PIP) install .

dev: _ensure_pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov ruff black isort pre-commit build twine

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m isort --check-only .
	$(PYTHON) -m black --check .
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m isort .
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check --fix .

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build

macos-app:
	@PYTHON="$(PYTHON)" bash packaging/macos/build_dmg.sh

macos-dmg: macos-app
