# Django Starter Template

A modern Django 5.2+ starter template with best practices, using **uv** for dependency management and **just** for task automation.

## Features

- **Django 5.2+** - Latest Django features and security updates
- **Custom User Model** - Pre-configured `CustomUser` extending `AbstractUser`
- **django-allauth** - Email-based authentication with social account support
- **uv** - Fast, modern Python package manager
- **Just** - Command runner for development tasks
- **Type Safety** - `ty` checks plus strict mypy configuration with django-stubs
- **Code Quality** - Ruff for linting/formatting, pre-commit hooks
- **Testing** - pytest with pytest-django and coverage reporting
- **Environment Configuration** - django-environ for 12-factor app compliance

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [Just](https://github.com/casey/just) - Install with `brew install just` (macOS)

### Command Invocation

This project organizes commands in Just modules.

- Use `just django <command>` for Django app operations
- Use `just <command>` for root development/QA commands
- Use `just docker <command>` for container workflows

### Option 1: Initialize a New Project (Recommended)

Use the included initialization script to set up a fresh project:

```bash
# Interactive mode
uv run init.py

# Non-interactive mode
uv run init.py --name my-project-name --description "My awesome Django project" --force
```

The initialization script will:

- Remove the existing git repository (unless `--skip-git` is used)
- Remove the virtual environment and database
- Create a new README.md with your project name
- Update pyproject.toml with your project details
- Prepare the project for a fresh start

After initialization:

```bash
rm init.py          # Remove the script
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
just django migrate
```

5. Create a superuser:

```bash
just django add-superuser
```

6. Start the development server:

```bash
just django serve
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to see your app running!

## 🛠️ Project Initialization Script

The included `init.py` script helps you quickly transform this template into your own project.

### Features

- **Interactive or Non-Interactive**: Run with or without command-line arguments
- **Clean Slate**: Removes git history, virtual environment, and database
- **Safety Gate**: Requires confirmation in interactive mode or `--force` in non-interactive mode before deleting existing state
- **Auto-Configuration**: Updates README.md and pyproject.toml with your project details
- **Rich UI**: Beautiful terminal interface with progress bars and colored output

### Usage

**Interactive Mode** (recommended for first-time users):

```bash
uv run init.py
```

You'll be prompted to enter:

- Project name (lowercase, with hyphens or underscores)
- Optional custom description

**Non-Interactive Mode**:

```bash
# Basic usage
uv run init.py --name my-awesome-project --force

# With description
uv run init.py --name my-awesome-project --description "A revolutionary Django app" --force

# Skip git repository removal
uv run init.py --name my-awesome-project --skip-git --force
```

### Command-Line Options

- `project_name` - Name of your new project (positional argument, optional)
- `--name` - Name of your new project (optional flag alternative)
- `--description, -d` - Custom project description
- `--skip-git` - Skip removing the git repository
- `--force` - Required for non-interactive runs that delete existing project state

### What It Does

1. **Removes existing git repository** - Clean slate for your version control
1. **Removes virtual environment** - Fresh Python environment
1. **Removes database file** - No leftover demo data
1. **Creates new README.md** - Customized with your project name and description
1. **Updates pyproject.toml** - Sets your project name and metadata

### After Initialization

Once the script completes, follow these steps:

```bash
# 1. Remove the initialization script (you won't need it anymore)
rm init.py

# 2. Initialize a new git repository
git init

# 3. Set up the environment
just init

# 4. Create your .env file (see Configuration section)

# 5. Run migrations
just django migrate

# 6. Start coding! 🎉
```

## 📋 Available Commands

### Django Commands

| Command                     | Description                                              |
| --------------------------- | -------------------------------------------------------- |
| `just django serve`         | Start Django development server                          |
| `just django migrate`       | Run migrations (automatically runs makemigrations first) |
| `just django add-superuser` | Create a superuser                                       |
| `just django shell`         | Start Django shell                                       |
| `just django deploy-check`  | Run Django deployment checks                             |
| `just django collectstatic` | Collect static files                                     |
| `just django new NAME`      | Create a new Django app with proper structure            |

### Development Commands

| Command            | Description                                       |
| ------------------ | ------------------------------------------------- |
| `just init`        | Set up environment (uv sync + pre-commit install) |
| `just update`      | Update all dependencies                           |
| `just clean`       | Remove temporary files and caches                 |
| `just fresh`       | Clean and reinstall everything                    |
| `just export-reqs` | Generate `requirements.txt` from `pyproject.toml` |

### Quality Assurance Commands

| Command      | Description                                       |
| ------------ | ------------------------------------------------- |
| `just lint`  | Run ruff linting and formatting                   |
| `just ty`    | Run type checks with `ty`                         |
| `just check` | Run lint, type checks, and pre-commit-stage hooks |
| `just test`  | Run pytest test suite                             |

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
```

Note: `LANGUAGE_CODE` is currently defined in `src/config/settings.py`.

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

Uses **ty** for routine checks (`just ty`) and maintains strict **mypy** configuration with django-stubs:

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

By default, `just check` runs pre-commit-stage hooks on all files.

Pre-commit stage hooks:

- djlint - Django template linting
- ruff - Python linting/formatting
- pyupgrade - Python 3.13+ syntax upgrades
- codespell - Spell checking
- detect-secrets - Secret detection

Pre-push/manual stage hooks:

- mypy - Type checking with django-stubs
- vulture - Unused code detection
- bandit - Security issue detection
- uv-secure - Dependency vulnerability scanning
- semgrep - Security rules scanning
- pytest - Test suite execution

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

## 🐳 Docker

Container commands are available via the Docker Just module:

```bash
# Build image
just docker build

# Run container locally
just docker run

# Build and run with Compose
docker compose up --build
```

## 🆕 Creating New Apps

Use the built-in command to create properly structured apps:

```bash
just django new blog
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

## 🤝 Contributing

1. Fork the repository
1. Create a feature branch: `git checkout -b feature/amazing-feature`
1. Run quality checks: `just check`
1. Run tests: `just test`
1. Commit your changes: `git commit -m 'Add amazing feature'`
1. Push to the branch: `git push origin feature/amazing-feature`
1. Open a Pull Request

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

______________________________________________________________________

**Happy coding! 🚀**
