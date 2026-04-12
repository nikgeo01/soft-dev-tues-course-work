# Doctor Visit Booking API

REST API for registering doctors and patients, managing working hours, and booking personal-doctor visits. Built with **FastAPI** and **SQLite** (see [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the full roadmap).

## Prerequisites

- **Python 3.9+** (Python **3.12+** recommended; use **3.10+** if you hit tooling issues with `mypy` / `pydantic-settings`)
- `make` (optional but used below)
- **Docker** and **Docker Compose** (optional, for containerized runs)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
make install                # upgrades pip/setuptools and installs the app in editable mode + dev tools
cp .env.example .env        # edit SECRET_KEY and other values as needed
mkdir -p data
make migrate                # apply Alembic migrations (Phase 1 includes an empty baseline)
```

## Run the API

```bash
make dev
# → http://127.0.0.1:8000  — interactive docs at /docs
```

Smoke check:

```bash
curl -s http://127.0.0.1:8000/health
# {"status":"ok"}
```

## Tests & quality

```bash
make test    # pytest + coverage
make lint    # ruff + mypy
make format  # ruff format + auto-fixes
```

## Docker

```bash
cp .env.example .env
mkdir -p data
docker compose up --build
```

The API is served on port **8000**. SQLite files are stored in the mounted `./data` directory.

## Project layout

- `app/` — FastAPI application (feature modules added in later phases)
- `alembic/` — database migrations
- `tests/` — automated tests
