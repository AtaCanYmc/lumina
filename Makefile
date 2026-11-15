.PHONY: help install dev test lint format clean build

PYTHON ?= python3
PIP ?= pip

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

install:
	$(PIP) install -r requirements.txt
	$(PIP) install .

dev:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov ruff black isort pre-commit build twine

test:
	pytest

lint:
	isort --check-only .
	black --check .
	ruff check .

format:
	isort .
	black .
	ruff check --fix .

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build
