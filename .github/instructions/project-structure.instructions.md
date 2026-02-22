---
name: Project Structure & File Ownership
description:
  Complete map of Django project layout (src/ root, src/config/ settings, app
  structure, template/static namespacing). Defines ownership boundaries, file
  inventory, when to use app-specific vs. shared resources, and Django best
  practices for template/static namespacing.
applyTo: '**'
---

# Project Structure Guide

Use this repository map when deciding where Django starter code should live.
This guide follows Django best practices for file organization, template/static
file namespacing, and clear ownership boundaries.

## Project Overview

This Django project uses a non-standard but well-organized structure:

- **Django root**: `src/` (not at repository root)
- **Settings module**: `src/config/` (not `projectname/`)
- **Management**: `src/manage.py`
- **Apps**: `src/<app>/` (users, web, etc.)

## Root-Level Files

Essential configuration and automation files at the repository root:

### Python Configuration

- `pyproject.toml`: Python dependencies, project metadata, and tool
  configuration (uv, pytest, mypy, etc.)
- `ruff.toml`: Ruff linting and formatting rules
- `mypy.ini`: Mypy type checking configuration
- `pytest.ini`: pytest-django settings
- `ty.toml`: ty type checker configuration

### Frontend Configuration

- `package.json`: Frontend CSS tooling scripts (Tailwind CSS)
- `tailwind.config.js`: Tailwind CSS and daisyUI theme configuration
- `postcss.config.js`: PostCSS pipeline for Tailwind

### Automation & Tooling

- `justfile`: Primary task runner entry point for all development commands
- `.pre-commit-config.yaml`: Git pre-commit hooks configuration
- `.env.example`: Required environment variables template (copy to `.env` for
  local development)
- `.gitignore`: Git ignore patterns
- `.python-version`: Python version specification for version managers

### Documentation & Scripts

- `README.md`: Project overview and setup instructions
- `AGENTS.md`: AI agent guidelines for code generation
- `DJANGO_VIBE_CODING_STARTER.md`: Comprehensive guide for replicating this
  pattern
- `init_project.py`: Initialization script for setting up new projects from this
  template
- `uv.lock`: Lock file for Python dependencies (managed by uv)

## Root-Level Directories

### `.github/`

GitHub-specific configuration and documentation:

- `.github/copilot-instructions.md`: GitHub Copilot instructions
- `.github/instructions/`: Detailed instruction files for different aspects of
  the project
  - `django-architecture.instructions.md`: Backend architecture rules
  - `frontend.instructions.md`: Frontend patterns
  - `htmx-cotton-patterns.instructions.md`: HTMX and django-cotton usage
  - `instructions.instructions.md`: Meta-guidelines for creating instruction
    files
  - `project-structure.instructions.md`: This file
  - `python.instructions.md`: Python coding standards
  - `tech-stack-dependencies.instructions.md`: Technology stack rules
  - `tools.instructions.md`: Development tooling guidelines

### `.agents/`

AI agent skills and capabilities:

- `.agents/skills/`: Domain-specific skill modules
  - `daisyui/`: DaisyUI component library knowledge
  - `htmx/`: HTMX development guidelines
  - `tailwind-design-system/`: Tailwind CSS design system patterns

### `.vscode/`

VS Code editor configuration (optional, may be gitignored)

### `data/`

Project-specific data files and configuration:

- `data/config/`: Configuration data
  - `colors.js`: Color scheme definitions

### `scripts/`

Automation scripts for development tasks:

- Utility scripts for generating metadata
- Database management helpers
- Deployment automation

### `tests/`

Top-level pytest test suite (recommended for cross-app and integration tests):

- `tests/conftest.py`: Shared pytest fixtures and configuration
- `tests/users/`: Tests for users app
- `tests/web/`: Tests for web app
- Additional test directories for each app

**Why top-level tests?**

- Facilitates integration testing across multiple apps
- Avoids import path complications
- Centralizes test configuration
- Mirrors pytest best practices

## Django Source Directory (`src/`)

All Django code lives in `src/` to keep the repository root clean.

### `src/manage.py`

Django's command-line utility. Run all Django commands from repository root:

```bash
uv run python src/manage.py <command>
```

### `src/config/`

Django settings module and project configuration:

```
src/config/
├── __init__.py           # Python package marker
├── settings.py           # Main Django settings (uses django-environ)
├── urls.py               # Root URL configuration
├── asgi.py              # ASGI configuration for async servers
└── wsgi.py              # WSGI configuration for production servers
```

**Key responsibilities:**

- Environment-based configuration (via `.env`)
- App registration split into `DJANGO_APPS`, `THIRD_PARTY_APPS`, `LOCAL_APPS`
- Middleware configuration
- Database, cache, email settings
- Authentication backend configuration (django-allauth)
- Static files and media configuration

**Pattern:**

```python
# src/config/settings.py
DJANGO_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', ...]
THIRD_PARTY_APPS = ['django_htmx', 'allauth', 'django_cotton', ...]
LOCAL_APPS = ['users', 'web']
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
```

### `src/users/`

Custom user model and authentication app:

```
src/users/
├── __init__.py
├── admin.py             # User admin configuration
├── apps.py             # App configuration
├── forms.py            # User forms (registration, profile, etc.)
├── models.py           # CustomUser model extending AbstractUser
├── urls.py             # User-specific URL patterns
├── views.py            # User-related views
├── tests.py            # App-level tests (optional, prefer top-level tests/)
├── migrations/         # Database migrations
│   ├── __init__.py
│   └── 0001_initial.py
├── templates/users/    # User app templates (namespaced)
│   ├── profile.html
│   └── settings.html
└── static/users/       # User app static files (namespaced)
    ├── css/
    └── js/
```

**Critical:** Always use `get_user_model()` or `settings.AUTH_USER_MODEL`, never
`django.contrib.auth.models.User`.

### `src/web/`

Default content/product app:

```
src/web/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── urls.py
├── views.py
├── tests.py
├── migrations/
│   └── __init__.py
├── templates/web/      # Web app templates (namespaced)
│   └── about.html
└── static/web/         # Web app static files (namespaced)
    ├── css/
    ├── js/
    └── images/
```

### `src/templates/`

Shared, cross-app templates:

```
src/templates/
├── _base.html                  # Base template for all pages
├── index.html                  # Homepage
├── partials/                   # Reusable template fragments
│   ├── navbar.html
│   ├── footer.html
│   └── messages.html
└── cotton/                     # django-cotton components
    ├── button.html
    ├── card.html
    └── modal.html
```

**Usage patterns:**

- **`_base.html`**: Defines the HTML shell with blocks for title, head,
  navigation, content, footer, scripts
- **`partials/`**: Included with `{% include 'partials/navbar.html' %}`
- **`cotton/`**: Invoked with `<c-button>` or `<c-card>` tags

**When to use shared vs app-specific templates:**

- **Shared** (`src/templates/`): Navigation, layouts, cross-app components
- **App-specific** (`src/<app>/templates/<app>/`): App domain logic, forms,
  detail pages

### `src/static/`

Shared, cross-app static files:

```
src/static/
├── css/
│   ├── input.css       # Tailwind CSS entry point
│   └── styles.css      # Compiled CSS output
├── js/
│   └── base.js         # Shared JavaScript
└── img/
    └── favicon.png
```

**Frontend pipeline:**

- Edit `input.css` with Tailwind directives
- Run `just css-dev` (watch mode) or `just css-build` (production)
- Output to `styles.css` (served via WhiteNoise in production)

## App Layout Conventions (Django Best Practices)

When creating new apps with `just new <app>`:

### Directory Structure

```
src/<app>/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── urls.py
├── views.py
├── forms.py              # Optional
├── services.py           # Optional: business logic layer
├── tests.py              # Optional: prefer top-level tests/
├── migrations/
│   └── __init__.py
├── templates/<app>/      # CRITICAL: Namespaced templates
│   └── *.html
└── static/<app>/         # CRITICAL: Namespaced static files
    ├── css/
    ├── js/
    └── images/
```

### Template Namespacing (Django Best Practice)

**Why namespace?** Django searches all `INSTALLED_APPS` for templates. Without
namespacing, two apps with `detail.html` would conflict.

**Correct:**

```
src/blog/templates/blog/detail.html
src/products/templates/products/detail.html
```

**Reference in views:**

```python
return render(request, 'blog/detail.html', context)
return render(request, 'products/detail.html', context)
```

**Incorrect:**

```
src/blog/templates/detail.html  # Will conflict with other apps
```

### Static File Namespacing (Django Best Practice)

**Why namespace?** Django's `AppDirectoriesFinder` collects static files from
all apps. Namespacing prevents collisions.

**Correct:**

```
src/blog/static/blog/style.css
src/products/static/products/app.js
```

**Reference in templates:**

```django
{% load static %}
<link rel="stylesheet" href="{% static 'blog/style.css' %}">
<script src="{% static 'products/app.js' %}"></script>
```

**Incorrect:**

```
src/blog/static/style.css  # Will conflict with other apps
```

### When to Use App-Specific vs Shared Files

| Type               | App-Specific                               | Shared                                           |
| ------------------ | ------------------------------------------ | ------------------------------------------------ |
| **Templates**      | Domain-specific pages, forms, detail views | Base layout, navigation, shared components       |
| **Static Files**   | App-specific styles, scripts, images       | Global CSS framework, shared utilities, favicons |
| **Business Logic** | Models, views, forms for one app           | Cross-app services, shared utilities             |

**Rule of thumb:** If it's used by more than one app, move it to shared. If it's
domain-specific, keep it in the app.

## URL Configuration and Ownership

### App URL Patterns

Each app defines its own `urls.py` with `app_name` for namespacing:

```python
# src/blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'  # Enables {% url 'blog:detail' pk=1 %}

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.detail, name='detail'),
]
```

### Root URL Configuration

`src/config/urls.py` only composes app routes:

```python
# src/config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Third-party
    path('blog/', include('blog.urls')),         # Local app
    path('', include('web.urls')),               # Default app
]
```

**Pattern:** Root URLs only route to apps and third-party packages, never define
views directly.

## Business Logic and Code Organization

### Keep Logic Close to Domain

- **Models**: Define in `models.py` within the app that owns the domain
- **Views**: Define in `views.py` within the app that handles the request
- **Forms**: Define in `forms.py` within the app that owns the form

### When to Extract to Services

Create `services.py` or shared utility modules when:

- Logic is reused across 2+ apps
- Business logic is complex and deserves separation from views
- You need to decouple from Django's request/response cycle

**Example:**

```python
# src/billing/services.py
def process_payment(user, amount):
    """Shared payment processing logic used by multiple apps."""
    # Complex logic here
    pass

# src/orders/views.py
from billing.services import process_payment

def checkout(request):
    process_payment(request.user, total)
    # ...
```

## Common Patterns

### Creating a New App

```bash
just new billing
```

This creates:

1. `src/billing/` with standard Django files
2. `src/billing/templates/billing/` (namespaced templates)
3. `src/billing/static/billing/` (namespaced static files)

**Next steps:**

1. Add `'billing'` to `LOCAL_APPS` in `src/config/settings.py`
2. Create `src/billing/urls.py` with `app_name = 'billing'`
3. Include in `src/config/urls.py`: `path('billing/', include('billing.urls'))`

### Organizing Templates

```
src/templates/
├── _base.html              # Global layout
├── index.html              # Homepage
├── partials/
│   ├── navbar.html         # {% include 'partials/navbar.html' %}
│   └── messages.html       # {% include 'partials/messages.html' %}
└── cotton/
    ├── button.html         # <c-button>Click me</c-button>
    └── card.html           # <c-card title="Hello">Content</c-card>

src/blog/templates/blog/
├── index.html              # {% extends '_base.html' %}
├── detail.html             # {% extends '_base.html' %}
└── _post_list.html         # {% include 'blog/_post_list.html' %}
```

**Naming conventions:**

- Partials: descriptive names, no prefix (e.g., `navbar.html`)
- Template fragments: prefix with `_` (e.g., `_post_list.html`)
- Base templates: prefix with `_` (e.g., `_base.html`)

### Organizing Static Files

```
src/static/
├── css/
│   ├── input.css           # Tailwind entry
│   └── styles.css          # Compiled output
├── js/
│   └── base.js             # Global scripts
└── img/
    └── favicon.png

src/blog/static/blog/
├── css/
│   └── blog.css            # Blog-specific styles
├── js/
│   └── comments.js         # Blog-specific scripts
└── images/
    └── placeholder.jpg
```

**Build commands:**

- Development: `just css-dev` (watch mode)
- Production: `just css-build` (minified)

## File Ownership Quick Reference

| File/Directory               | Owner   | Purpose                                |
| ---------------------------- | ------- | -------------------------------------- |
| `pyproject.toml`             | Project | Python dependencies and tool config    |
| `justfile`                   | Project | Task automation                        |
| `.env` / `.env.example`      | Project | Environment configuration              |
| `src/config/`                | Project | Django settings and root URLs          |
| `src/templates/`             | Project | Shared templates, partials, components |
| `src/static/`                | Project | Shared static files                    |
| `src/<app>/`                 | App     | App-specific code and domain logic     |
| `src/<app>/templates/<app>/` | App     | App-specific templates (namespaced)    |
| `src/<app>/static/<app>/`    | App     | App-specific static files (namespaced) |
| `tests/`                     | Project | Cross-app integration tests            |
| `.github/instructions/`      | Project | AI agent and Copilot guidelines        |
| `.agents/skills/`            | Project | AI agent domain skills                 |

## Summary of Key Conventions

1. **Django root in `src/`**: All Django code in `src/`, not at repository root
2. **Namespace templates and static**: Always use `<app>/templates/<app>/` and
   `<app>/static/<app>/`
3. **App ownership**: Each app owns its models, views, templates, and URLs
4. **Root URLs compose**: `src/config/urls.py` only includes app routers
5. **Shared vs specific**: Shared files in `src/templates/` and `src/static/`,
   app-specific in app directories
6. **Custom user model**: Always use `get_user_model()`, never `User` directly
7. **Business logic**: Keep close to domain; extract to services only when
   reused
8. **Testing**: Prefer top-level `tests/` for integration tests
9. **Task automation**: Use `just` for all development commands

## References

- Django Official Documentation:
  [Writing your first Django app](https://docs.djangoproject.com/en/6.0/intro/)
- Django Best Practices:
  [Static file namespacing](https://docs.djangoproject.com/en/6.0/intro/tutorial06/#static-file-namespacing)
- Django Best Practices:
  [Template namespacing](https://docs.djangoproject.com/en/6.0/intro/tutorial03/#namespacing-url-names)
