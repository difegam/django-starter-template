# Settings & Environment

This project uses **django-environ** to load all configuration from environment variables, following the [Twelve-Factor App](https://12factor.net/) methodology. No secrets should ever appear in version control.

## How configuration works

1. Django loads `config.settings` (set via `DJANGO_SETTINGS_MODULE` in `pyproject.toml`)
1. `django-environ` reads your `.env` file (local development) or real environment variables (production)
1. Settings use `env('VARIABLE_NAME')` to read values with type casting and defaults

## Settings file

All settings live in a single file: `src/config/settings.py`. The key sections are:

| Section            | What it configures                                                                      |
| ------------------ | --------------------------------------------------------------------------------------- |
| **Core**           | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SECURE_SSL_REDIRECT`   |
| **Auth backends**  | `ModelBackend` + `allauth.account.auth_backends.AuthenticationBackend`                  |
| **Installed apps** | Django core + allauth + local apps (`config`, `users`, `web`)                           |
| **Middleware**     | SecurityMiddleware → WhiteNoiseMiddleware → SessionMiddleware → ... → AccountMiddleware |
| **Database**       | `DATABASE_URL` parsed into Django's `DATABASES` dict                                    |
| **Static files**   | `STORAGES` → WhiteNoise `CompressedManifestStaticFilesStorage`, `STATIC_ROOT`           |
| **Email**          | `EMAIL_URL` parsed into Django's email settings                                         |
| **Auth**           | `AUTH_USER_MODEL = 'users.CustomUser'`, login/redirect URLs                             |
| **allauth**        | Email-only login, session remember, unique email                                        |

## Environment variables

### Core

| Variable                 | Required | Default               | Description                                                |
| ------------------------ | -------- | --------------------- | ---------------------------------------------------------- |
| `SECRET_KEY`             | **Yes**  | —                     | Django secret key. Generate with `openssl rand -base64 48` |
| `DEBUG`                  | No       | `True`                | Enable debug mode. Set `False` for production              |
| `ALLOWED_HOSTS`          | No       | `localhost,127.0.0.1` | Comma-separated list of allowed hostnames                  |
| `DJANGO_SETTINGS_MODULE` | No       | `config.settings`     | Python path to settings module                             |

### Security

| Variable                         | Required | Default                                       | Description                                           |
| -------------------------------- | -------- | --------------------------------------------- | ----------------------------------------------------- |
| `CSRF_TRUSTED_ORIGINS`           | No       | `http://localhost:8000,http://127.0.0.1:8000` | Comma-separated trusted origins for POST/PUT/DELETE   |
| `SECURE_SSL_REDIRECT`            | No       | `False`                                       | Redirect all HTTP to HTTPS. Enable behind a TLS proxy |
| `SECURE_HSTS_SECONDS`            | No       | `0`                                           | Browser HSTS duration in seconds                      |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | No       | `False`                                       | Include subdomains in HSTS policy                     |
| `SECURE_HSTS_PRELOAD`            | No       | `False`                                       | Opt in to browser HSTS preload lists                  |
| `SESSION_COOKIE_SECURE`          | No       | `False`                                       | Send session cookies over HTTPS only                  |
| `CSRF_COOKIE_SECURE`             | No       | `False`                                       | Send CSRF cookies over HTTPS only                     |
| `SECURE_CONTENT_TYPE_NOSNIFF`    | No       | `True`                                        | Add `X-Content-Type-Options: nosniff`                 |

### Database

| Variable            | Required | Default                    | Description                                                                       |
| ------------------- | -------- | -------------------------- | --------------------------------------------------------------------------------- |
| `DATABASE_URL`      | No       | `sqlite:///src/db.sqlite3` | Django database connection URL. PostgreSQL: `postgres://user:pass@db:5432/dbname` |
| `POSTGRES_DB`       | No       | `django_db` in Compose     | PostgreSQL container database name; Django does not read this directly            |
| `POSTGRES_USER`     | No       | `postgres` in Compose      | PostgreSQL container username; Django does not read this directly                 |
| `POSTGRES_PASSWORD` | No       | `postgres` in Compose      | PostgreSQL container password; Django does not read this directly                 |
| `POSTGRES_HOST`     | No       | `db` by convention         | PostgreSQL host to use inside `DATABASE_URL` when using Docker Compose            |
| `POSTGRES_PORT`     | No       | `5432` by convention       | PostgreSQL port to use inside `DATABASE_URL`                                      |

For Docker Compose with the bundled PostgreSQL service, set Django's database connection explicitly:

```env
DATABASE_URL=postgres://postgres:postgres@db:5432/django_db
```

### Email

| Variable    | Required | Default                         | Description                                                       |
| ----------- | -------- | ------------------------------- | ----------------------------------------------------------------- |
| `EMAIL_URL` | No       | `console://` (prints to stdout) | Email connection URL. Production: `smtp+tls://user:pass@host:587` |

### Internationalization

| Variable        | Required | Default | Description                                                                                         |
| --------------- | -------- | ------- | --------------------------------------------------------------------------------------------------- |
| `TIME_ZONE`     | No       | `UTC`   | Default timezone ([IANA identifiers](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)) |
| `LANGUAGE_CODE` | No       | `en-us` | Default language (ISO 639-1)                                                                        |

### Auth URLs

| Variable             | Required | Default            | Description                                 |
| -------------------- | -------- | ------------------ | ------------------------------------------- |
| `LOGIN_URL`          | No       | `/accounts/login/` | Login page path (used by `@login_required`) |
| `LOGIN_REDIRECT_URL` | No       | `home`             | Redirect target after login (URL name)      |

### Superuser (optional)

| Variable                         | Required | Default | Description                                                           |
| -------------------------------- | -------- | ------- | --------------------------------------------------------------------- |
| `DJANGO_SUPERUSER_USERNAME`      | No       | —       | Auto-create superuser on Docker entrypoint                            |
| `DJANGO_SUPERUSER_EMAIL`         | No       | —       | Superuser email                                                       |
| `DJANGO_SUPERUSER_PASSWORD`      | No       | —       | Superuser password (**dev only** — never commit)                      |
| `DJANGO_SUPERUSER_PASSWORD_FILE` | No       | —       | Read password from file (production, e.g. `/run/secrets/su_password`) |

### Platform

| Variable | Required | Default | Description                                                       |
| -------- | -------- | ------- | ----------------------------------------------------------------- |
| `PORT`   | No       | `8000`  | Gunicorn bind port. Most PaaS platforms inject this automatically |

## Using django-environ

All environment variables are read through `django-environ`'s typed accessors:

```python
import environ

env = environ.Env(
    DEBUG=(bool, False),
    TIME_ZONE=(str, 'UTC'),
)

# Reading .env file (local development only)
environ.Env.read_env(BASE_DIR.parent / '.env')

# Usage examples
SECRET_KEY = env('SECRET_KEY')  # string, required
DEBUG = env('DEBUG')  # bool, default False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[...])  # comma-separated → list
DATABASES = {'default': env.db_url('DATABASE_URL', default=...)}  # URL → Django DB dict
EMAIL_URL = env.email_url('EMAIL_URL')  # URL → email settings dict
```

## Setting DJANGO_SETTINGS_MODULE

By default, `DJANGO_SETTINGS_MODULE` is set in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = 'config.settings'
```

And in `src/config/wsgi.py` / `src/config/asgi.py`:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```

If you need environment-specific settings, set `DJANGO_SETTINGS_MODULE` to a different path:

- **Local dev**: keep `config.settings` in `pyproject.toml` (the default)
- **Docker/production**: set `DJANGO_SETTINGS_MODULE=config.settings` in your environment (the same module reads env vars differently depending on the environment)

## Security checklist for production

- [ ] `SECRET_KEY` is a long, random string (never reuse across environments)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` includes your production domain(s)
- [ ] `CSRF_TRUSTED_ORIGINS` includes `https://yourdomain.com`
- [ ] `SECURE_SSL_REDIRECT=True` (behind a TLS proxy)
- [ ] `SECURE_HSTS_SECONDS=31536000` (only after confirming HTTPS works end-to-end)
- [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- [ ] `SECURE_HSTS_PRELOAD=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_CONTENT_TYPE_NOSNIFF=True`
- [ ] `.env` file is never committed to version control
- [ ] Database credentials use a strong, unique password
- [ ] `EMAIL_URL` points to a real SMTP server

## Reference

- Full `.env.example` with all variables and explanations: [`.env.example`](../.env.example)
- django-environ documentation: https://django-environ.readthedocs.io/
- Django settings reference: https://docs.djangoproject.com/en/6.0/ref/settings/
