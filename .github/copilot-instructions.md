# Copilot Instructions

## Architecture Overview

This is a Django 5.2+ starter template with a **non-standard project layout**: Django lives in `src/`, with `src/config/` as the settings module (not a `projectname/` package). All commands run from the repo root via `just` and `uv`.

**Stack**: Django templates (server-rendered) + HTMX + django-cotton components + Alpine.js + Tailwind CSS v4 + daisyUI 5. Authentication via django-allauth. No REST API — this is a hypermedia-driven app.

## Project Layout

- `src/config/` — Django settings, root URLs, WSGI/ASGI (replaces the typical `projectname/` directory)
- `src/<app>/` — Django apps (`users`, `web`); each app owns its models, views, URLs, and namespaced templates/static
- `src/templates/` — Shared templates: `_base.html`, `partials/`, `cotton/` components
- `src/static/` — Shared static: `css/input.css` (Tailwind entry), `css/output.css` (compiled), `js/`, `img/`
- `tests/` — Top-level pytest suite (cross-app integration tests, not inside apps)
- `.github/instructions/` — Detailed domain-specific instruction files (architecture, frontend, HTMX patterns, Python style, etc.)

## Essential Commands

```bash
just init          # Install Python deps (uv sync), npm deps, pre-commit hooks
just serve         # Run dev server (uv run python src/manage.py runserver)
just test          # Run pytest on tests/
just lint          # Ruff check --fix + format
just ty            # Type check with ty
just check         # lint + ty + pre-commit on all files
just migrate       # makemigrations + migrate
just new <name>    # Create new app in src/ with namespaced templates/static dirs
just css-dev       # Watch + compile Tailwind CSS
just css-build     # Production Tailwind CSS build
```

## Critical Conventions

**Custom User Model**: Always use `get_user_model()` or `settings.AUTH_USER_MODEL`, never `from django.contrib.auth.models import User`. The custom model is `users.CustomUser` extending `AbstractUser`.

**Template Namespacing**: App templates must live in `src/<app>/templates/<app>/` to avoid cross-app collisions. Reference as `'<app>/template.html'` in views.

**Static Namespacing**: App static files in `src/<app>/static/<app>/`. Reference with `{% static '<app>/file.css' %}`.

**Views**: Use function-based views with type hints (`def my_view(request: HttpRequest) -> HttpResponse:`). Check `request.htmx` to return partial fragments vs full pages.

**HTMX + Partials**: Use `{% partialdef %}` (Django 6.0) or `django-template-partials` for fragment rendering. Return `template.html#fragment_name` for HTMX requests.

**Cotton Components**: Reusable UI in `src/templates/cotton/`. Use `<c-component>` syntax. Components are purely presentational — no DB queries.

**CSRF**: Set globally on `<body hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'>` in `_base.html`.

## Frontend Pipeline

Tailwind CSS v4 configured CSS-first in `src/static/css/input.css` (uses `@import 'tailwindcss'`, `@plugin 'daisyui'`, `@source` directives for template scanning). The `tailwind.config.js` is minimal — configuration lives in the CSS file. daisyUI component classes (`btn`, `card`, `hero`, etc.) are preferred over raw Tailwind for UI elements.

## Adding a New App

1. `just new billing` (creates app with namespaced dirs in `src/`)
2. Add `'billing'` to `LOCAL_APPS` in `src/config/settings.py`
3. Create `src/billing/urls.py` with `app_name = 'billing'`
4. Include in `src/config/urls.py`: `path('billing/', include('billing.urls'))`
5. Add `tests/billing/__init__.py` for tests

## Code Quality

- Python 3.13+, type hints required on all new functions
- Ruff for linting/formatting (120 char line length, migrations excluded)
- `uv` for dependency management (`pyproject.toml`), never pip directly
- Environment config via `.env` + `django-environ` (see `.env.example`)
- `INSTALLED_APPS` split into `DJANGO_APPS`, `THIRD_PARTY_APPS`, `LOCAL_APPS`
