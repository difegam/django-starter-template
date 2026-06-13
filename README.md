# Django Starter Template

A modern Django 6 starter template with best practices, using **uv** for dependency management and **just** for task automation.

## Features

- **Django 6** - Latest Django features and security updates
- **Custom User Model** - Pre-configured `CustomUser` extending `AbstractUser`
- **django-allauth** - Email-based authentication with social account support
- **uv** - Fast, modern Python package manager
- **Just** - Command runner for development tasks
- **Type Safety** - `ty` for static type checking with django-stubs
- **Code Quality** - Ruff for linting/formatting, prek-managed Git hooks
- **Testing** - pytest with pytest-django and coverage reporting
- **Environment Configuration** - django-environ for 12-factor app compliance
- **Docker** - Multi-stage builds, Caddy reverse proxy, Cloudflare integration

## Quick start

Use this section based on what you are doing:

- **Creating a new project from this template?** Follow the recommended path below and run `./init.py` first.
- **Working on this template repository directly?** Skip to [local development setup](#local-development-setup).

For detailed instructions, including Windows setup, see **[docs/quickstart.md](docs/quickstart.md)**.

### Create a new project from this template

#### 1. Clone the template

```bash
git clone <your-repo-url> my-project
cd my-project
```

#### 2. Run the one-time initializer

The initializer turns the starter template into your project. It prompts for a project name, optional description, and cleanup choices.

```bash
./init.py
```

When cleanup choices appear, use **Space** to toggle options and **Enter** to continue.

If direct execution fails, run the script through `uv`:

```bash
uv run init.py
```

Preview planned changes without modifying files:

```bash
./init.py --name my-project --dry-run
```

Run non-interactively:

```bash
./init.py --name my-project --force
```

> [!WARNING]
> `./init.py` can remove local template state such as `.git`, `.venv`, caches, `node_modules`, `.DS_Store`, and `src/db.sqlite3`.
> Run with `--dry-run` first if you want to inspect planned changes before deleting anything.

What `./init.py` does:

- Updates `README.md` with your project name and description.
- Updates `pyproject.toml` project metadata.
- Removes selected local/template artifacts so the new project starts clean.
- Prints next steps for creating a fresh Git repository and starting development.

### Local development setup

Use these commands after running `./init.py`, or when working on this template repository directly.

#### 1. Create your environment file

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
SECRET_KEY=<generate with: openssl rand -base64 48>
DEBUG=True
DATABASE_URL=sqlite:///src/db.sqlite3
```

#### 2. Install dependencies and hooks

```bash
just init
```

#### 3. Run migrations and start the server

```bash
just django migrate
just django serve
```

Visit **http://127.0.0.1:8000**.

## Available commands

### Django commands

| Command                     | Description                                              |
| --------------------------- | -------------------------------------------------------- |
| `just django serve`         | Start Django development server                          |
| `just django migrate`       | Run migrations (automatically runs makemigrations first) |
| `just django add-superuser` | Create a superuser                                       |
| `just django shell`         | Start Django shell                                       |
| `just django deploy-check`  | Run Django deployment checks                             |
| `just django collectstatic` | Collect static files                                     |
| `just django new NAME`      | Create a new Django app with proper structure            |

### Development commands

| Command             | Description                                       |
| ------------------- | ------------------------------------------------- |
| `just init`         | Set up environment (uv sync + prek install)       |
| `just update`       | Update all dependencies                           |
| `just clean`        | Remove temporary files and caches                 |
| `just fresh`        | Clean and reinstall everything                    |
| `just hooks-update` | Update prek hook revisions                        |
| `just export-reqs`  | Generate `requirements.txt` from `pyproject.toml` |

### Quality assurance commands

| Command      | Description                                                |
| ------------ | ---------------------------------------------------------- |
| `just lint`  | Run ruff linting and formatting                            |
| `just ty`    | Run type checks with `ty`                                  |
| `just check` | Run lint, type checks, and prek-managed commit-stage hooks |
| `just test`  | Run pytest test suite                                      |

## Configuration

The project uses `django-environ` to load all configuration from environment variables. Copy `.env.example` to `.env` and set at minimum:

```env
SECRET_KEY=<generate with: openssl rand -base64 48>
DEBUG=True
DATABASE_URL=sqlite:///src/db.sqlite3
```

See **[docs/settings.md](docs/settings.md)** for the full environment variable reference.

## Authentication

Configured with django-allauth for email-only login (no username). Social login (GitHub, Google, etc.) is ready to enable via Django admin.

See **[docs/authentication.md](docs/authentication.md)** for allauth configuration, social login setup, and email verification options.

## Custom user model

This template ships with a custom user model from day one (`users.CustomUser`). Always reference it indirectly:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
```

See **[docs/users.md](docs/users.md)** for extending the user model with custom fields.

## Testing

```bash
just test                                # run all tests
uv run pytest --cov=src --cov-report=html  # with HTML coverage
```

See **[docs/testing.md](docs/testing.md)** for writing model, view, and form tests, and CI setup.

## Deployment

This project supports multiple deployment targets:

- **Docker Compose + Caddy** (Hetzner, DigitalOcean VPS)
- **Dokploy** (self-hosted PaaS)
- **Railway** (managed PaaS)
- **Fly.io** (managed PaaS)
- **Cloudflare** (DNS, proxy, TLS)

```bash
# Production deploy with Docker Compose
just deploy-production
```

See **[docs/deployment.md](docs/deployment.md)** for full deployment guides.

## Creating new apps

```bash
just django new blog
```

Creates `src/blog/` with standard Django app files, templates, and static directories. Don't forget to add the app to `LOCAL_APPS` in `src/config/settings.py`.

## Contributing

See **[docs/contributing.md](docs/contributing.md)** for dependency management, code style, and PR guidelines.

```bash
just check   # run all quality checks before opening a PR
just test    # run tests
```

## Dependencies

### Core

- **Django 6** - Web framework
- **django-allauth** - Authentication with social accounts
- **django-environ** - Environment variable management
- **gunicorn** - WSGI HTTP server
- **whitenoise** - Static file serving

### Development

- **pytest** & **pytest-django** - Testing framework
- **pytest-cov** - Coverage reporting
- **ty** & **django-stubs** - Type checking
- **ruff** - Fast linter and formatter
- **prek** - Git hook management
- **django-debug-toolbar** - Debug panel for development

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

Built with modern Python tooling:

- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [Just](https://just.systems/) - Command runner
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- [Django](https://www.djangoproject.com/) - The web framework for perfectionists

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [django-allauth Documentation](https://docs.allauth.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Just Manual](https://just.systems/)
