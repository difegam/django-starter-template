# Django Starter Template

## What is this?

A production-ready Django 6 starter template built on modern Python tooling: **uv** for dependency management, **Just** for task automation, **Ruff** for linting, **ty** for type checking, **pytest** for testing, and **django-allauth** for authentication. It ships with a custom user model, Tailwind/DaisyUI frontend, Docker deployment with Caddy or Traefik, and Cloudflare integration — all wired up and ready to go.

This template is designed for **small-to-medium projects** where you want a solid, maintainable foundation without the overhead of a larger meta-template.

______________________________________________________________________

## Design decisions

Every choice in this template was made with learning and long-term maintainability in mind:

| Decision                           | Rationale                                                                                                                                                                                                                                                                |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`src/` layout**                  | Encourages treating your Django apps as proper Python packages. Avoids accidental imports from the working directory. Matches the modern Python packaging standard.                                                                                                      |
| **Custom User Model from day one** | Django's own docs [recommend this](https://docs.djangoproject.com/en/6.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project). Changing the user model after the first migration is complex and risky — this template removes that pain entirely. |
| **uv over pip/poetry/pipenv**      | Significantly faster dependency resolution and installation. Deterministic lockfile. No separate virtual environment management step — `uv sync` handles everything.                                                                                                     |
| **Just over Make**                 | Single, discoverable task runner with readable syntax. Cross-platform (macOS, Linux, Windows). No shell escaping issues.                                                                                                                                                 |
| **Ruff over flake8/black/isort**   | One tool replaces multiple linters and formatters. 10–100x faster. Enforces consistent style including import sorting.                                                                                                                                                   |
| **django-environ for config**      | Follows the [Twelve-Factor App](https://12factor.net/) principle: all configuration via environment variables. No secrets in code.                                                                                                                                       |
| **django-allauth for auth**        | Battle-tested authentication library with email-only login, social providers, account management views, and email verification — all included.                                                                                                                           |
| **WhiteNoise for static files**    | Serves static files directly from Gunicorn. No need for Nginx or a separate static file server in most deployments.                                                                                                                                                      |
| **pytest over unittest**           | Fixtures, markers, parametrize, better assertion introspection. pytest-django provides `client`, `db`, `admin_user`, and other Django-specific fixtures.                                                                                                                 |

______________________________________________________________________

## Comparison with other templates

### vs. [Cookiecutter Django](https://github.com/cookiecutter/cookiecutter-django)

| Aspect               | This template                      | Cookiecutter Django                                              |
| -------------------- | ---------------------------------- | ---------------------------------------------------------------- |
| **Setup complexity** | Low — one `just init`              | High — 30+ prompts during project creation                       |
| **Frontend opinion** | Tailwind + DaisyUI (default)       | Generic (Bootstrap or none)                                      |
| **Tooling**          | uv + Just + Ruff + ty + pytest     | pip + Docker + Celery + Sentry (all optional)                    |
| **Code quality**     | Prek hooks (pre-commit + pre-push) | Optional pre-commit                                              |
| **Best for**         | Small teams, learning, fast start  | Large teams needing many integrations (Celery, Sentry, Channels) |

### vs. [wemake-django-template](https://github.com/wemake-services/wemake-django-template)

| Aspect                | This template                                     | wemake-django-template                                |
| --------------------- | ------------------------------------------------- | ----------------------------------------------------- |
| **Style enforcement** | Moderate — Ruff with sensible defaults            | Very strict — flake8 plugins, mypy, many custom rules |
| **Deployment**        | Flexible — Caddy or Traefik, multiple PaaS guides | Fixed — Traefik only                                  |
| **Learning curve**    | Low — familiar Django conventions                 | High — custom project conventions, many layers        |
| **Best for**          | Teams that want quality without ceremony          | Teams wanting extreme code quality enforcement        |

### When to choose this template

- You want a **fast, modern start** with sensible defaults
- Your project is small-to-medium sized (blog, SaaS MVP, internal tool)
- You value **learning and maintainability** over maximal configuration
- You prefer **uv + Just + Ruff + pytest** as your toolchain
- You want Docker deployment with **Caddy or Traefik** without deep configuration

### When NOT to choose this template

- You need Celery, Channels, Sentry, or extensive third-party integrations from the start → **use Cookiecutter Django**
- You want extremely strict code style enforcement and custom project conventions → **use wemake-django-template**
- You need a team of 10+ developers with complex CI/CD pipelines → **use Cookiecutter Django**

______________________________________________________________________

## Project structure

```
├── src/                        # Django project root (src layout)
│   ├── config/                 # Project configuration
│   │   ├── settings.py         # All Django settings (django-environ)
│   │   ├── urls.py             # Root URL configuration
│   │   ├── wsgi.py             # WSGI application
│   │   └── asgi.py             # ASGI application
│   ├── users/                  # Custom User app (CustomUser model)
│   ├── web/                    # Main web app (home page)
│   ├── templates/              # Shared templates (allauth overrides)
│   ├── static/                 # Static assets (CSS, JS, images)
│   └── manage.py               # Django management command
├── tests/                      # Test suite (pytest)
│   ├── conftest.py             # Shared fixtures (user, admin_user, etc.)
│   ├── users/                  # User model tests
│   └── web/                    # Web view tests
├── docs/                       # Project documentation
├── Docker/                     # Docker build files
│   ├── Dockerfile              # Multi-stage build (dev + production)
│   ├── caddy/                  # Caddy reverse proxy
│   └── entrypoint.sh           # Container entrypoint
├── docker-compose.yml          # Local development stack
├── docker-compose.production.yml  # Production stack
├── Caddyfile.prod               # Production Caddy reverse proxy config
├── Caddyfile.local              # Local dev Caddy config (self-signed certs)
├── justfile                    # Task runner (Just)
├── pyproject.toml              # Project metadata & dependencies
├── .env.example                # Environment variable reference
└── ruff.toml                   # Linter/formatter config
```

______________________________________________________________________

## Getting started

See [Quick Start](quickstart.md) for step-by-step instructions.

______________________________________________________________________

## Further reading

- [Quick Start](quickstart.md) — get up and running
- [Settings & Environment](settings.md) — configure your project
- [User Model](users.md) — custom user setup and extension points
- [Authentication](authentication.md) — allauth, social logins, custom user
- [Testing](testing.md) — write and run tests
- [Deployment](deployment.md) — Docker, Caddy, Cloudflare, production
- [Contributing](contributing.md) — maintain dependencies and code quality
