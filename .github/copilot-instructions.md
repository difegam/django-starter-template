# Copilot Instructions

## Architecture

Django 5.2+ project rooted in `src/` with `config/` as the Django settings module (not a typical `project_name/` layout). All Django commands run from `src/` via `uv run python src/manage.py`.

- **`src/config/`** — settings, root URLs, ASGI/WSGI. Settings use `django-environ` to read `.env` from project root.
- **`src/users/`** — custom user model (`CustomUser` extends `AbstractUser`). Always use `get_user_model()` or `settings.AUTH_USER_MODEL`, never `django.contrib.auth.models.User`.
- **`src/web/`** — example app serving pages. New apps go in `src/` via `just new NAME`.
- **`src/templates/`** — project-wide templates. Apps own templates at `src/<app>/templates/<app>/`.
- **`src/templates/cotton/`** — reusable Cotton components used across pages with `<c-*>` syntax.
- **`src/static/`** — project-wide static files. Apps own static at `src/<app>/static/<app>/`.
- **`tests/`** — top-level pytest suite with `conftest.py` (`DJANGO_SETTINGS_MODULE = config.settings`).

## Key Commands

All dev commands use `just` (task runner) + `uv` (package manager):

```
just init          # uv sync + npm install + pre-commit install
just serve         # runserver
just migrate       # makemigrations + migrate
just test          # pytest -vv --tb=short -s tests/
just lint          # ruff check --fix + ruff format
just ty            # ty type checker
just check         # lint + ty + pre-commit hooks
just security      # bandit + detect-secrets + pip-audit
just css-dev       # Tailwind watch mode
just css-build     # Tailwind minified production build
just new NAME      # scaffold new app in src/ with template/static dirs
```

## Coding Conventions

- **Python 3.13+**, max line length 120, 4-space indent, single quotes preferred.
- **Type hints required** on all new functions (params + return types). See `src/web/views.py` for the pattern: `def home(request: HttpRequest) -> HttpResponse`.
- **URL patterns**: each app defines `app_name` and `urlpatterns`; include in `src/config/urls.py`.
- **Settings structure**: `INSTALLED_APPS` is split into `DJANGO_APPS`, `THIRD_PARTY_APPS`, `LOCAL_APPS` lists.
- **Auth**: django-allauth handles authentication (email-based login). Allauth URLs at `/accounts/`. `django.contrib.sites` enabled with `SITE_ID = 1`.

## Frontend Stack

Server-rendered Django templates enhanced with HTMX, Alpine.js, Tailwind CSS + daisyUI:

- Base template: `src/templates/_base.html` — loads HTMX via `{% htmx_script %}`, Alpine.js via CDN, includes daisyUI from CDN, sets CSRF header globally via `hx-headers`.
- Standard blocks: `title`, `head`, `navigation`, `content`, `footer`, `scripts`.
- Partials: `src/templates/partials/` (e.g., `navbar.html`). Use `{% include %}` for partials.
- Cotton components: place in `src/templates/cotton/`, use with `<c-*>` syntax.
- Use daisyUI component classes (`btn`, `card`, `navbar`, `hero`, etc.) with Tailwind utilities.
- Alpine.js for local UI state only (dropdowns, modals, toggles). Use `x-cloak` to prevent FOUC.
- HTMX for partial page updates; return fragment templates for `HX-Request`, full pages otherwise.

## Testing

- Framework: `pytest` + `pytest-django`. Configuration in `pytest.ini` with `DJANGO_SETTINGS_MODULE = config.settings` and `pythonpath = src`.
- `conftest.py` at `tests/` root.
- Test directories: `tests/web/`, `tests/users/`.
- Test files: `tests/<app>/test_*.py` with `test_` prefixed functions.
- Run: `just test` or `uv run pytest -vv --tb=short -s tests/`.

## Pre-commit & Quality Gates

Pre-commit hooks enforce: Ruff lint/format, `detect-secrets`, `bandit`, `uv-secure`, `codespell`, `shellcheck`. Run `just check` before committing. Run `just security` for dedicated security scans. Ruff config is in `ruff.toml` (excludes migrations, templates, static files).

## Production Readiness

- WhiteNoise middleware serves static files in production.
- Gunicorn available as WSGI server (`gunicorn config.wsgi:application --chdir src`).
- PostgreSQL support via `psycopg` (configure `DATABASE_URL` env var).
- Run `just css-build` to compile minified CSS before deploy.
