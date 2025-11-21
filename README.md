# Django Starter Template

A modern Django 5.2+ starter template with best practices, using **uv** for dependency management and **just** for task automation.

##  Features

- **Django 5.2+** - Latest Django features and security updates
- **Custom User Model** - Pre-configured `CustomUser` extending `AbstractUser`
- **django-allauth** - Email-based authentication with social account support
- **uv** - Fast, modern Python package manager
- **Just** - Command runner for development tasks
- **Type Safety** - Full mypy strict mode with django-stubs
- **Code Quality** - Ruff for linting/formatting, pre-commit hooks
- **Testing** - pytest with pytest-django and coverage reporting
- **Environment Configuration** - django-environ for 12-factor app compliance

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [Just](https://github.com/casey/just) - Install with `brew install just` (macOS)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd django-starter-template
```

2. Set up the environment:
```bash
just install
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
just dj-migrate
```

5. Create a superuser:
```bash
just dj-superuser
```

6. Start the development server:
```bash
just run
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to see your app running!

## 📋 Available Commands

### Django Commands

| Command | Description |
|---------|-------------|
| `just run` | Start Django development server |
| `just dj-migrate` | Run migrations (automatically runs makemigrations first) |
| `just dj-superuser` | Create a superuser |
| `just dj-shell` | Start Django shell |
| `just dj-check` | Run Django deployment checks |
| `just dj-collectstatic` | Collect static files |
| `just new-app NAME` | Create a new Django app with proper structure |

### Development Commands

| Command | Description |
|---------|-------------|
| `just install` | Set up environment (uv sync + pre-commit install) |
| `just update` | Update all dependencies |
| `just clean` | Remove temporary files and caches |
| `just fresh` | Clean and reinstall everything |
| `just export-requirements` | Generate requirements.txt from pyproject.toml |

### Quality Assurance Commands

| Command | Description |
|---------|-------------|
| `just lint` | Run ruff linting and formatting |
| `just check` | Run mypy and all pre-commit hooks |
| `just test` | Run pytest test suite |


## 🔧 Configuration

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

Uses **mypy** in strict mode with django-stubs:

- All functions require type hints
- `disallow_untyped_defs=True`
- Django plugin enabled

Example:
```python
from django.http.request import HttpRequest
from django.http.response import HttpResponse

def my_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'template.html')
```

### Pre-commit Hooks

Automatically run on every commit (or manually with `just check`):

- djlint - Django template linting
- ruff - Python linting/formatting
- pyupgrade - Python 3.13+ syntax upgrades
- codespell - Spell checking
- bandit - Security issue detection
- detect-secrets - Secret detection
- uv-secure - Dependency vulnerability scanning

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
just new-app blog
```

This creates:
- `src/blog/` directory with standard Django app files
- `src/blog/templates/blog/` for app-specific templates
- `src/blog/static/blog/` for app-specific static files

**Don't forget to add the new app to `LOCAL_APPS` in `src/config/settings.py`:**

```python
LOCAL_APPS = [
    'users',
    'demo',
    'blog',  # Add your new app here
]
```

## 📦 Dependencies

### Core Dependencies

- **Django 5.2+** - Web framework
- **django-allauth** - Authentication with social accounts
- **django-environ** - Environment variable management

### Development Dependencies

- **pytest** & **pytest-django** - Testing framework
- **pytest-cov** - Coverage reporting
- **mypy** & **django-stubs** - Type checking
- **ruff** - Fast linter and formatter
- **pre-commit** - Git hook management
- **django-debug-toolbar** - Debug panel for development

## 🐳 Docker Support

Docker commands are available in the justfile:

```bash
just build          # Build Docker images
just dive IMAGE     # Explore Docker image layers
```

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

**Happy coding! 🚀**
