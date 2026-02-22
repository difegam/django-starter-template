# Repository Guidelines

A production-ready Django starter template providing pre-configured authentication, component-based server-rendered UI, and modern Python tooling — so new projects skip boilerplate and start building features immediately.

## Architecture Overview

This project uses a **non-standard Django layout** where all Django code lives under `src/` and the settings module is `src/config/` (not a `projectname/` package). This keeps the repo root clean for tooling configs while Django remains self-contained.

**Rendering model**: Server-rendered HTML via Django templates. HTMX handles partial page updates, django-cotton provides reusable components, Alpine.js adds lightweight interactivity. There is **no REST API** and no SPA — this is a hypermedia-driven application.

**Data flow**: Browser → Django view (checks `request.htmx`) → returns full page or HTML fragment → HTMX swaps fragment into DOM. CSRF is handled globally via `<body hx-headers>` in `_base.html`.

**Authentication**: django-allauth provides email-based auth at `/accounts/`. The custom user model (`users.CustomUser` extending `AbstractUser`) is set from day one to avoid painful migration issues later.

## Template Patterns Decision Guide

**Django template partials** (Django 6.0+ built-in `{% partialdef %}`): Use for HTMX-swappable fragments within a single page. Partials inherit the current template context and can be rendered via `render(request, 'template.html#partial_name', context)`. Ideal for page-specific fragments that won't be reused elsewhere.

**Cotton components** (`<c-button>`, `<c-card>` in `src/templates/cotton/`): Use for cross-app reusable UI building blocks with explicit props, slots, and attribute forwarding via `{{ attrs }}`. Components are purely presentational—no DB queries or business logic. Ideal for design system primitives used across 3+ templates.

**Include partials** (`{% include 'partials/navbar.html' %}`): Use for static template composition like navbars, footers, and sidebars. Non-interactive content that's same across pages.

**Practical rule**: Partials for page-local fragments + HTMX targets, Cotton for your reusable design system, includes for static composition.

## Critical File Inventory

| Component | File Path | Description & Purpose | Why It's Critical |
|-----------|-----------|----------------------|-------------------|
| Entry Point | `src/manage.py` | Django CLI entry point | All commands run via `uv run python src/manage.py` |
| Settings | `src/config/settings.py` | All Django config; reads `.env` via `django-environ` | `INSTALLED_APPS` split into `DJANGO_APPS` / `THIRD_PARTY_APPS` / `LOCAL_APPS`; defines `AUTH_USER_MODEL` |
| Root URLs | `src/config/urls.py` | Composes app routers; never defines views directly | Add new app routes here after `just new <app>` |
| Custom User | `src/users/models.py` | `CustomUser(AbstractUser)` — the project's user model | Always reference via `get_user_model()`, never `django.contrib.auth.models.User` |
| User Admin | `src/users/admin.py` | Custom admin with `CustomUserCreationForm` / `CustomUserChangeForm` | Pattern to follow when extending user fields |
| User Forms | `src/users/forms.py` | `AdminUserCreationForm` / `UserChangeForm` subclasses | Wired into admin; extend these when adding user fields |
| Example View | `src/web/views.py` | `home()` — typed FBV returning `render(request, 'index.html')` | Reference pattern for all new views |
| Base Template | `src/templates/_base.html` | HTML shell: loads HTMX (`{% htmx_script %}`), Alpine (CDN), Tailwind CSS; sets global CSRF header | All pages `{% extends "_base.html" %}`; blocks: `title`, `head`, `navigation`, `content`, `footer`, `scripts` |
| Homepage | `src/templates/index.html` | Extends `_base.html`, uses daisyUI `hero` component | Example of template inheritance + daisyUI classes |
| Navbar Partial | `src/templates/partials/navbar.html` | daisyUI navbar with allauth links | Example partial included via `{% include %}` |
| Tailwind Entry | `src/static/css/input.css` | `@import 'tailwindcss'`, `@plugin 'daisyui'`, `@source` directives, `@theme` tokens | CSS-first config (not `tailwind.config.js`); edit here for themes/colors |
| Task Runner | `justfile` | All dev commands (`serve`, `test`, `lint`, `migrate`, `new`, etc.) | Primary interface — never run raw Django/npm commands |
| Python Deps | `pyproject.toml` | Runtime + dev dependencies managed by `uv` | `uv sync` to install; never use `pip install` directly |
| Frontend Deps | `package.json` | Tailwind CLI + daisyUI + Prettier | `npm run dev` / `npm run build` (or use `just css-dev` / `just css-build`) |
| Linter Config | `ruff.toml` | 120-char lines, single quotes, extensive rule set including `DJ` (Django), `S` (security), `ANN` (annotations) | Excludes migrations, templates, static, `__init__.py` |
| Type Checker | `ty.toml` | ty config with Django-aware overrides for tests/settings | Relaxed rules for `tests/**` and `settings.py` |
| Pre-commit | `.pre-commit-config.yaml` | djLint, Ruff, pyupgrade, codespell, bandit, detect-secrets, uv-secure, shellcheck | Runs on `just check`; validates security + formatting |
| Env Template | `.env.example` | Required env vars: `SECRET_KEY`, `DATABASE_URL`, `DEBUG`, etc. | Copy to `.env` for local dev |
| Test Config | `tests/conftest.py` | Sets `DJANGO_SETTINGS_MODULE = config.settings` and calls `django.setup()` | pytest discovers this automatically |

## Build, Test, and Development Commands

Use `just` for all tasks — it loads `.env` automatically (`set dotenv-load := true`):

```bash
just init          # uv sync --all-groups + npm install + pre-commit install
just serve         # Django dev server (runserver)
just test          # pytest -vv --tb=short -s tests/
just lint          # ruff check --fix + ruff format
just ty            # ty type checker
just check         # lint + ty + pre-commit run --all-files
just migrate       # makemigrations + migrate (chained)
just new <name>    # startapp in src/ + create namespaced template/static dirs
just css-dev       # Tailwind watch mode (input.css → output.css)
just css-build     # Tailwind minified production build
just shell         # Django shell
just add-superuser # createsuperuser
just deploy-check  # Django deployment checklist
just collectstatic # Collect static files for production
just clean         # Remove .venv, caches, __pycache__
just fresh         # clean + init (full reset)
```

Coverage: `uv run pytest --cov=src --cov-report=html`

## Coding Conventions

### Python
- **Python 3.13+**, 4-space indent, **120-char line length**, single quotes (enforced by Ruff)
- **Type hints required** on all new/changed functions: `def view(request: HttpRequest) -> HttpResponse:`
- **Function-based views** preferred; delegate business logic to service functions or querysets
- Imports: `get_user_model()` or `settings.AUTH_USER_MODEL` — never `from django.contrib.auth.models import User`
- App names: lowercase, descriptive (e.g., `billing`, `notifications`)

### Templates
- **Namespace everything**: app templates in `src/<app>/templates/<app>/`, static in `src/<app>/static/<app>/`
- Shared templates in `src/templates/`: `_base.html`, `partials/`, `cotton/`
- Cotton components (`<c-button>`, `<c-card>`) for reusable UI — purely presentational, no DB queries
- Use Django 6.0+ built-in `{% partialdef %}` for HTMX-swappable fragments within full-page templates (no `{% load %}` tag needed)

### Frontend
- daisyUI component classes (`btn`, `card`, `hero`, `navbar`) preferred over raw Tailwind utilities
- Theme config via `@theme` block in `input.css`, not in `tailwind.config.js`
- Alpine.js for micro-interactions; use `x-cloak` to prevent FOUC

### HTMX Pattern

```python
# Standard view pattern: full page vs HTMX partial
def item_list(request: HttpRequest) -> HttpResponse:
    items = Item.objects.all()
    template = 'items/list.html'
    if request.htmx:
        template += '#item-table'  # Render only the partialdef fragment
    return render(request, template, {'items': items})
```

## Adding a New App

```bash
just new billing                          # Creates src/billing/ with namespaced dirs
```

Then:
1. Add `'billing'` to `LOCAL_APPS` in `src/config/settings.py`
2. Create `src/billing/urls.py` with `app_name = 'billing'`
3. Add `path('billing/', include('billing.urls'))` to `src/config/urls.py`
4. Create `tests/billing/__init__.py`

## Testing
- Framework: `pytest` + `pytest-django` + `pytest-cov`
- Tests in top-level `tests/` directory (not inside apps) — organized by app: `tests/users/`, `tests/web/`
- Config in `tests/conftest.py`: sets `DJANGO_SETTINGS_MODULE = config.settings`
- Test files: `test_*.py`; test functions: `test_*`
- Run: `just test`

## Security & Pre-commit Pipeline

Pre-commit hooks run automatically on `just check` and include:
- **djLint**: Django template linting and formatting
- **Ruff**: Python lint + format
- **pyupgrade**: Modernize syntax to Python 3.13+
- **codespell**: Catch typos
- **bandit**: Python security scanning (excludes `tests/`)
- **detect-secrets**: Prevent credential leaks
- **uv-secure**: Scan `uv.lock` for vulnerable dependencies
- **shellcheck**: Shell script linting

Keep secrets in `.env`; never commit credentials. Use `# scan:ignore` comment to suppress false positives in detect-secrets.

## Commit Messages

Concise, imperative mood: `Fix user profile redirect`, `Add billing app`, `feat: implement payment flow`.
PRs should include validation steps (`just check`, `just test`), screenshots for UI changes, and callouts for migrations, breaking changes, or new env vars.
