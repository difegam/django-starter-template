# Django Starter Template - AI Coding Agent Guide

## Project Architecture

This is a Django 5.2+ starter template using **uv** for dependency management and **Just** for task automation. The codebase follows a modular structure with the Django project located in `src/`.

### Key Structure

- `src/config/` - Django settings and URL configuration
- `src/users/` - Custom user model (extends AbstractUser)
- `src/web/` - Example app demonstrating the structure
- `src/templates/` - Project-wide templates with `_base.html` as the base template
- `src/static/` - Project-wide static files (css/, js/, img/)
- `tests/` - Top-level test directory (not inside src/)

### Custom User Model

This project uses a **custom user model** (`users.CustomUser`) from the start. Always reference `AUTH_USER_MODEL` or import `CustomUser` from `users.models` instead of Django's default User model.

## Critical Workflows

### Project Initialization

If starting a new project from this template, run `./init.py` (or `uv run init.py`):

- Run interactively for prompts, or pass `project_name` as argument
- Removes git repo, venv, and database for fresh start
- Creates new README.md and updates pyproject.toml
- After running, delete the script and run `just init`

### Development Commands (via Just)

This project uses Just modules. Use `just django <command>` for Django app operations.

**Django Commands:**

- `just django serve` - Start Django dev server
- `just django migrate` - Run migrations (auto-runs makemigrations first)
- `just django add-superuser` - Create a superuser
- `just django shell` - Start Django shell
- `just django new NAME` - Create new Django app with proper structure
- `just django deploy-check` - Run Django deployment checks
- `just django collectstatic` - Collect static files

**Quality Assurance:**

- `just lint` - Run ruff linting and formatting
- `just ty` - Run ty type checker (Astral's mypy alternative)
- `just check` - Run lint + ty + prek-managed commit-stage hooks
- `just test` - Run pytest suite with verbose output

**Development:**

- `just init` - Set up environment (uv sync + prek install)
- `just update` - Update all dependencies
- `just clean` - Remove temp files, caches, venv
- `just fresh` - Clean + init for fresh setup
- `just hooks-update` - Update prek hook revisions
- `just export-reqs` - Generate requirements.txt from pyproject.toml

**Important**: Always use `uv run python src/manage.py <command>` or the `just` recipes. Never run `django-admin` or bare `python` commands.

### Creating New Apps

Use `just django new NAME` which:

1. Creates the app in `src/` directory
1. Sets up `templates/NAME/` and `static/NAME/` directories
1. Reminds you to add it to `LOCAL_APPS` in `src/config/settings.py`

**Always add new apps to `LOCAL_APPS`** (not `INSTALLED_APPS` directly).

### Environment Configuration

Uses `django-environ` with `.env` file in project root. The `.env` file is read from `BASE_DIR.parent` (one level above `src/`).

Required variables:

- `SECRET_KEY` - Django secret key
- `DEBUG` - Boolean for debug mode
- `ALLOWED_HOSTS` - Comma-separated list (defaults to localhost,127.0.0.1)
- `TIME_ZONE` - Timezone string (defaults to UTC)
- `DATABASE_URL` - Database connection (defaults to `sqlite:///src/db.sqlite3`)

## Code Quality Standards

### Python Style (Ruff)

- **Single quotes** for strings (enforced by ruff formatter)
- Line length: 120 characters
- Target: Python 3.13
- Migrations, templates, static files, `__init__.py`, and `manage.py` excluded from linting
- Comprehensive ruleset including Django-specific rules (DJ), security (S), and performance (PERF)

### Type Checking (mypy + ty)

**mypy** (django-stubs integration):

- **Strict mode enabled** with django-stubs plugin
- All functions require type hints (disallow_untyped_defs=True)
- mypy_path points to `./src`
- Migrations and tests excluded from type checking

**ty** (Astral's type checker):

- Python 3.13+ targeted
- Checks `manage.py`, `src/`, and `tests/`
- Errors on unresolved imports/references, invalid assignments
- Warns on unused-ignore-comment and redundant-cast
- Relaxed rules for tests and settings files
- Run with `just ty`

### Prek Hooks

Commit-stage hooks run automatically on commit and via `just check`.
Pre-push/manual hooks run on `pre-push` or `manual` stages.

- djlint for Django templates (reformatting + linting)
- ruff for Python linting/formatting
- pyupgrade (Python 3.13+ syntax)
- codespell (spelling checker)
- detect-secrets (prevents committing secrets)
- shellcheck (shell script linting)
- Standard hooks (trailing whitespace, file size, YAML/JSON/TOML validation)

Pre-push/manual hooks include:

- mypy (type checking)
- vulture (unused code detection)
- bandit (security scanning)
- uv-secure (dependency vulnerability scanning)
- semgrep (security scanning)
- pytest (test suite)

## Project-Specific Conventions

### Authentication

Uses **django-allauth** with email-only authentication:

- `ACCOUNT_LOGIN_METHODS = {'email'}` - No username login
- `ACCOUNT_UNIQUE_EMAIL = True` - Email must be unique
- Login redirects to `home` URL name
- Allauth URLs mounted at `/accounts/`
- **Password minimum length: 12 characters** (not Django's default 8)

### Type Annotations

All view functions must be annotated:

```python
from django.http.request import HttpRequest
from django.http.response import HttpResponse

def my_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'template.html')
```

### App Structure Convention

Each Django app follows this structure:

```
app_name/
├── templates/app_name/    # App-specific templates
├── static/app_name/        # App-specific static files
├── migrations/
├── models.py
├── views.py
├── urls.py
├── admin.py
└── tests.py
```

### Settings Organization

Settings are split logically in `src/config/settings.py`:

- `DJANGO_APPS` - Django built-in apps
- `THIRD_PARTY_APPS` - External packages (allauth, etc.)
- `LOCAL_APPS` - Project apps (config, users, web, etc.)
- Final `INSTALLED_APPS = [*DJANGO_APPS, *THIRD_PARTY_APPS, *LOCAL_APPS]`

**Always add new apps to `LOCAL_APPS`**, not directly to `INSTALLED_APPS`.

### Environment Variables Pattern

Uses `django-environ` with typed defaults in settings:

```python
env = environ.Env(
    DEBUG=(bool, False),
    TIME_ZONE=(str, 'UTC'),
)
env.read_env(BASE_DIR.parent / '.env')
```

## Testing

Uses pytest with pytest-django:

- Run via `just test` or `uv run pytest`
- Tests located in `tests/` directory (top-level, not inside src/)
- Coverage reporting enabled with pytest-cov
- Test output: verbose mode with short traceback (`-vv --tb=short -s`)

## Common Pitfalls

1. **Don't forget** to add new apps to `LOCAL_APPS` in settings
1. **Always use** `uv run` prefix for Python commands
1. **Migrations are auto-generated** by `just django migrate` (don't run makemigrations separately)
1. **Custom user model** is already set - don't import Django's User model
1. **Single quotes** are enforced - use 'string' not "string"
1. **Static/template directories** must exist in each app (created by `just django new NAME`)
1. **Environment file location** - `.env` must be in project root, not in `src/`
