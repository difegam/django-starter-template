# Django Vibe Coding Starter

A modern Django 6.0+ starter template with best practices, using **uv** for dependency management and **just** for task automation. It includes a custom user model, django-allauth for authentication, and a strong set of development tools for linting, type checking, testing, and more. Get a new Django project running in seconds.

Frontend assets use **Tailwind CSS v4** and **daisyUI 5**, with a simple npm setup for building and watching CSS changes. The structure is designed for scalability and maintainability, with clear separation between configuration, apps, components, and utilities.

**HTMX** enables dynamic partial page updates, while **Alpine.js** adds lightweight interactivity. Combined with Django templates, partials, and django-cotton, you can build reusable UI components with ease.

## Features

- **Django 6.0+** - Latest Django features and security updates
- **Custom User Model** - Pre-configured `CustomUser` extending `AbstractUser`
- **django-allauth** - Email-based authentication with social account support
- **HTMX + Alpine.js** - Dynamic, hypermedia-driven user interfaces
- **Tailwind CSS v4 + daisyUI 5** - Modern, utility-first CSS framework with semantic components
- **uv** - Fast, modern Python package manager
- **Just** - Command runner for development tasks (Python and frontend)
- **Type Safety** - `ty` for Python type checking
- **Code Quality** - Ruff for linting/formatting, pre-commit hooks, ESLint for JavaScript
- **Testing** - pytest with pytest-django and coverage reporting
- **Environment Configuration** - django-environ for 12-factor app compliance

## Project Structure

- `src/config/` - Settings, ASGI/WSGI, root URLs
- `src/users/` - Custom user model and auth-related code
- `src/web/` - Example app for site pages
- `src/templates/` and `src/static/` - Shared templates and assets
- `tests/` - Top-level pytest suite (app tests in `tests/web/`, `tests/users/`)

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+ and npm 10+ (for frontend tooling)
- [uv](https://github.com/astral-sh/uv) - Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [Just](https://github.com/casey/just) - Install with `brew install just` (macOS)

### Option 1: Initialize a New Project (Recommended)

Use the included initialization script to set up a fresh project:

```bash
# Interactive mode
uv run init_project.py

# Non-interactive mode
uv run init_project.py my-project-name --description "My awesome Django project"
```

The initialization script will:
- Remove the existing git repository (unless `--skip-git` is used)
- Remove the virtual environment and database
- Create a new README.md with your project name
- Update pyproject.toml with your project details
- Prepare the project for a fresh start

After initialization:
```bash
rm init_project.py  # Remove the script
git init            # Initialize new git repo
just init           # Set up environment
```

### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd django-starter-template
```

2. Set up the environment:
```bash
just init
```

3. Create a `.env` file in the project root:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=UTC
DATABASE_URL=sqlite:///src/db.sqlite3
```

4. Run migrations:
```bash
just migrate
```

5. Create a superuser:
```bash
just add-superuser
```

6. Start the development server:
```bash
just serve
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to see your app running.

## 🛠️ Project Initialization Script

The included `init_project.py` script transforms this template into your own project.

**Usage**
```bash
# Interactive mode
uv run init_project.py

# Non-interactive mode
uv run init_project.py my-awesome-project --description "A Django app"

# Skip git repository removal
uv run init_project.py my-awesome-project --skip-git
```

**What it does**
- Removes git history, virtual environment, and the demo database
- Updates `README.md` and `pyproject.toml` with your project details

**After initialization**
```bash
rm init_project.py
git init
just init
just migrate
```

## 📋 Available Commands

### Django Commands

| Command | Description |
|---------|-------------|
| `just serve` | Start Django development server |
| `just migrate` | Run migrations (automatically runs makemigrations first) |
| `just add-superuser` | Create a superuser |
| `just shell` | Start Django shell |
| `just deploy-check` | Run Django deployment checks |
| `just collectstatic` | Collect static files |
| `just new NAME` | Create a new Django app with proper structure |

### Development Commands

| Command | Description |
|---------|-------------|
| `just init` | Set up environment (uv sync + npm install + pre-commit install) |
| `just update` | Update all dependencies |
| `just clean` | Remove temporary files and caches |
| `just fresh` | Clean and reinstall everything |
| `just export-reqs` | Generate `requirements.txt` from `pyproject.toml` |

### Frontend CSS Commands

| Command | Description |
|---------|----------|
| `npm run css:dev` | Watch and compile Tailwind CSS (includes daisyUI) |
| `npm run css:build` | Production build of Tailwind CSS (minified) |
| `npm run lint` | Lint JavaScript files |
| `npm run lint:fix` | Auto-fix JavaScript linting issues |
| `npm run format` | Format all code with Prettier |
| `npm run format:check` | Check code formatting without modifying |

### Quality Assurance Commands

| Command | Description |
|---------|-------------|
| `just lint` | Run ruff linting and formatting |
| `just ty` | Run type checks with `ty` |
| `just check` | Run lint, type checks, and all pre-commit hooks |
| `just test` | Run pytest test suite |

## 🔧 Configuration

### Tailwind Theme Usage

Theme tokens are defined in `src/static/css/input.css` using Tailwind v4 `@theme`. This generates utilities like `bg-primary`, `text-secondary-dark`, and `border-primary-light`.

```html
<button class="bg-primary text-white hover:bg-primary-dark px-4 py-2 rounded">
  Primary
</button>

<div class="bg-primary-lighter text-primary-darker p-4 rounded">
  Primary tint
</div>

<a class="text-secondary hover:text-secondary-dark underline">
  Secondary link
</a>
```

### Environment Variables

The project uses `django-environ` for configuration. Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///src/db.sqlite3
# For PostgreSQL: DATABASE_URL=postgres://user:password@localhost:5432/dbname

# Localization
TIME_ZONE=UTC
LANGUAGE_CODE=en-us
```

### Custom User Model

This template uses a custom user model from the start (`users.CustomUser`). Always reference:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Or import directly
from users.models import CustomUser
```

**Never import Django's default User model.**

### Authentication

Configured with django-allauth for email-based authentication:

- Email-only login (no username)
- Social account integration ready
- Login URL: `/accounts/login/`
- Logout URL: `/accounts/logout/`
- Redirects after login: `home` URL name

## 🎨 Code Quality

### Linting and Formatting

Uses **Ruff** for fast Python linting and formatting:

- Single quotes enforced
- 120 character line length
- Python 3.13 target
- Auto-fix on `just lint`

### Type Checking

Uses **ty** for type checks (`just ty`). Configuration lives in `ty.toml` and includes Django-aware paths and test overrides.

Example:
```python
from django.http.request import HttpRequest
from django.http.response import HttpResponse

def my_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'template.html')
```

### Pre-commit Hooks

Automatically run on every commit (or manually with `just check`):

- pre-commit hooks - whitespace, YAML/JSON/TOML checks, and file hygiene
- djlint - Django template linting + formatting
- ruff - Python linting/formatting
- pyupgrade - Python 3.13+ syntax upgrades
- codespell - Spell checking
- bandit - Security issue detection
- detect-secrets - Secret detection
- uv-secure - Dependency vulnerability scanning
- shellcheck - Shell script static analysis

## 🧪 Testing

Uses **pytest** with pytest-django:

```bash
# Run all tests
just test

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_specific.py -vv
```

Tests are located in the top-level `tests/` directory.

## 🆕 Creating New Apps

Use the built-in command to create properly structured apps:

```bash
just new blog
```

This creates:
- `src/blog/` directory with standard Django app files
- `src/blog/templates/blog/` for app-specific templates
- `src/blog/static/blog/` for app-specific static files

**Don't forget to add the new app to `LOCAL_APPS` in `src/config/settings.py`:**

```python
LOCAL_APPS = [
    'users',
    'web',
    'blog',  # Add your new app here
]
```

## 📦 Dependencies

### Python - Core Dependencies

- **Django 6.0+** - Web framework
- **django-allauth** - Authentication with social accounts
- **django-environ** - Environment variable management
- **django-cotton** - Component-based template rendering
- **django-htmx** - HTMX support utilities
- **whitenoise** - Static file serving
- **gunicorn** - Production WSGI server

### Python - Development Dependencies

- **pytest** & **pytest-django** - Testing framework
- **pytest-cov** - Coverage reporting
- **ty** - Type checking
- **django-stubs** - Better type hints for Django APIs
- **ruff** - Fast linter and formatter
- **pre-commit** - Git hook management
- **django-debug-toolbar** - Debug panel for development

### Frontend - Runtime Dependencies

- **HTMX** (`htmx.org`) - High power interactions for HTML
- **Alpine.js** (`alpinejs`) - Lightweight JavaScript framework for interactivity

### Frontend - Development Dependencies

- **Tailwind CSS v4** - Utility-first CSS framework
- **daisyUI v5** - Pre-built Tailwind CSS component library
- **ESLint** - JavaScript linting
- **Prettier** - Code formatter with Tailwind CSS plugin for class sorting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run quality checks: `just check`
4. Run tests: `just test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

Built with modern Python tooling:
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [Just](https://github.com/casey/just) - Command runner
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- [Django](https://www.djangoproject.com/) - The web framework for perfectionists

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [django-allauth Documentation](https://docs.allauth.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Just Manual](https://just.systems/)

---

Happy coding!
