# Repository Guidelines

## Project Structure & Module Organization

This is a Django project using a `src/` layout. The Django project package lives in `src/config/`, with settings, URLs, ASGI, and WSGI entry points. Application code is split into `src/web/` and `src/users/`; add new apps under `src/<app_name>/`.

Shared templates are in `src/templates/`, including account templates and partials. Static assets live in `src/static/` (`css/`, `js/`, and `img/`). The main pytest suite is under `tests/`, organized by app, with shared fixtures in `tests/conftest.py`. Project docs live in `docs/`, and Docker-related files are in `Docker/` plus `docker-compose.yml`.

## Build, Test, and Development Commands

- `just --list`: show available root and module recipes.
- `just init`: install dependencies with `uv sync --all-groups` and install `prek` hooks.
- `just django migrate`: create and apply Django migrations.
- `just django serve`: run the local Django development server.
- `just django new NAME`: create a new Django app under `src/`.
- `just lint`: run Ruff checks with safe fixes, then format code.
- `just ty`: run `ty` type checks.
- `just test`: run the pytest suite in `tests/`.
- `just check`: run linting, type checks, and all `prek` hooks.

## Coding Style & Naming Conventions

Use Python 3.13+. Ruff enforces 4-space indentation, 120-character lines, single-quoted strings, import sorting, and Django lint rules. Prefer type annotations for new Python code. Name Django apps and Python modules with lowercase snake_case; name test files `test_*.py`.

Templates are checked by `djlint` through `prek`; keep reusable fragments in `src/templates/partials/`. Do not commit generated caches, virtualenvs, or local database files.

## Testing Guidelines

Tests use `pytest`, `pytest-django`, and settings from `config.settings`. Place app tests in `tests/<app>/`, and put reusable fixtures in `tests/conftest.py`. Run focused tests with examples like `uv run pytest tests/web/test_home.py`. No coverage threshold is currently enforced.

## Commit & Pull Request Guidelines

Recent history uses Conventional Commit-style prefixes such as `feat:`, `chore:`, `docs:`, and `test:`. Keep messages imperative and scoped to one change.

Before opening a PR, run `just check` and `just test`. PR descriptions should state the intent, link related issues when available, and call out migrations, environment variable changes, or security-sensitive configuration changes. Include screenshots for visible template or static asset changes.

## Security & Configuration Tips

Use `.env.example` as the configuration reference, but never commit real `.env` secrets. Keep `DEBUG=False` outside local development, set `ALLOWED_HOSTS` explicitly, and run `just django deploy-check` before production-oriented changes.
