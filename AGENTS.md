# Repository Guidelines

## Project Structure & Module Organization
The Django project lives in `src/`:
- `src/config/`: settings, ASGI/WSGI, root URLs.
- `src/users/`: custom user model and auth-related code.
- `src/web/`: example app for site pages.
- `src/templates/` and `src/static/`: shared templates and assets.
- `tests/`: top-level pytest suite (preferred for cross-app/integration tests).

Keep app-specific templates and static files under `src/<app>/templates/<app>/` and `src/<app>/static/<app>/` when adding new apps (`just new NAME` scaffolds this).

## Build, Test, and Development Commands
Use `just` recipes for daily work:
- `just init`: install dependencies with `uv sync --all-groups`, `npm install`, and install pre-commit hooks.
- `just serve`: run Django dev server.
- `just migrate`: create and apply migrations.
- `just test`: run pytest with verbose output.
- `just lint`: run Ruff lint + format.
- `just ty`: run static type checks with `ty`.
- `just check`: run lint, types, and all pre-commit hooks.
- `just security`: run bandit, detect-secrets, and pip-audit.
- `just css-dev`: watch and compile Tailwind CSS for development.
- `just css-build`: build and minify Tailwind CSS for production.

Example flow: `just init && just migrate && just serve`.

## Coding Style & Naming Conventions
- Python 3.13+, 4-space indentation, max line length 120.
- Ruff enforces formatting; use single quotes where possible.
- Add type hints to new/changed Python code (especially views and service functions).
- Use descriptive Django app names in lowercase (e.g., `billing`, `notifications`).
- Do not use Django’s default `User`; use `users.CustomUser` / `get_user_model()`.

## Testing Guidelines
- Framework: `pytest` + `pytest-django` (+ `pytest-cov` when needed).
- Configuration in `pytest.ini` with `DJANGO_SETTINGS_MODULE = config.settings` and `pythonpath = src`.
- `conftest.py` at `tests/` root.
- Test directories: `tests/web/`, `tests/users/`.
- Test files should follow `test_*.py`; test functions should start with `test_`.
- Run all tests with `just test`.
- Optional coverage run: `uv run pytest --cov=src --cov-report=html`.

## Commit & Pull Request Guidelines
Recent history favors concise, imperative commit messages (e.g., `Fix ...`, `Add ...`), with occasional Conventional Commit prefixes (`feat:`). Keep subject lines clear and specific.

For PRs:
- Explain what changed and why.
- Link related issues/tasks.
- Include validation steps run (`just check`, `just test`).
- Add screenshots for UI/template changes.
- Call out migrations, breaking changes, or new env vars explicitly.

## Security & Configuration Tips
- Keep secrets in `.env`; never commit credentials.
- Run pre-commit locally before pushing.
- `detect-secrets`, `bandit`, and `uv-secure` are enforced via hooks; address findings before opening a PR.
