.PHONY: install dev test lint format migrate migration

# Prefer project venv when present so `make test` works after `make install`.
PYTHON := $(shell if [ -x .venv/bin/python3 ]; then echo .venv/bin/python3; else command -v python3; fi)

install:
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -e ".[dev]"

dev:
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy app

format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

migrate:
	mkdir -p data
	$(PYTHON) -m alembic upgrade head

migration:
	@read -p "Migration message: " msg; $(PYTHON) -m alembic revision --autogenerate -m "$$msg"
