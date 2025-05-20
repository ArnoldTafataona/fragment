# Makefile for a Python project using Poetry and src/ layout
# Assumes `poetry config virtualenvs.in-project true`

VENV_PATH=.venv
PYTHON=$(VENV_PATH)/bin/python
MAIN=src/fragment/__main__.py
SRC=src
TESTS=tests

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@echo "  setup       Install dependencies using Poetry (creates .venv locally)"
	@echo "  cleanup     Remove virtual environment and Python cache files"
	@echo "  freeze      Export dependencies to requirements.txt"
	@echo "  run         Run the application using Poetry"
	@echo "  test        Run tests using pytest"
	@echo "  lint        Run flake8 for linting"
	@echo "  format      Format code using black"
	@echo "  typecheck   Check type hints using mypy"
	@echo "  check       Run formatting, linting, type checks, and tests"
	@echo "  help        Show this help message"

.PHONY: setup
setup:
	@poetry install
	@echo "Installing development tools (flake8, black, mypy, pytest)..."
	@poetry add --group dev flake8 black mypy pytest

.PHONY: cleanup
cleanup:
	@echo "Removing .venv..."
	@rm -rf $(VENV_PATH)
	@echo "Removing __pycache__ and .pyc files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

.PHONY: freeze
freeze:
	@poetry export -f requirements.txt --without-hashes -o requirements.txt
	@echo "Exported dependencies to requirements.txt"

.PHONY: run
run:
	@poetry run $(PYTHON) $(MAIN)

.PHONY: test
test:
	@poetry run pytest $(TESTS)

.PHONY: lint
lint:
	@poetry run flake8 $(SRC)

.PHONY: format
format:
	@poetry run black $(SRC)

.PHONY: typecheck
typecheck:
	@poetry run mypy $(SRC)

.PHONY: check
check: format lint typecheck test
