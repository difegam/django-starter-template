# Deployment

## Overview

This project uses a `src/` layout with Gunicorn as the WSGI server. All configuration is driven by environment variables via `django-environ`.

**WSGI entry point:** `config.wsgi:application` (with `--chdir src`)
**Settings module:** `config.settings`
**Web server:** Gunicorn (already included in dependencies)

The following deployment platforms are covered:

- **Dokploy** — Self-hosted PaaS (Docker-based, Traefik reverse proxy)
- **Railway** — Managed PaaS (Nixpacks auto-detection)
- **Fly.io** — Managed PaaS (Docker-based)
- **Hetzner VPS** — Docker Compose + Caddy
- **DigitalOcean** — Docker Compose + Caddy (or App Platform)

______________________________________________________________________

## Prerequisites

- Python 3.13+
- `uv` (https://docs.astral.sh/uv/)
- A domain name with DNS pointing to your server
- Platform tools:
  - **Dokploy:** Web dashboard
  - **Railway:** `railway` CLI (optional)
  - **Fly.io:** `flyctl` CLI
  - **Hetzner / DigitalOcean:** SSH access

______________________________________________________________________

## Shared Configuration

### Environment Variables

| Variable                 | Description                     | Required          | Default                    |
| ------------------------ | ------------------------------- | ----------------- | -------------------------- |
| `SECRET_KEY`             | Django secret key               | Yes               | —                          |
| `DEBUG`                  | Debug mode                      | No                | `False`                    |
| `ALLOWED_HOSTS`          | Comma-separated hostnames       | No                | `localhost,127.0.0.1`      |
| `DATABASE_URL`           | Database connection string      | No                | `sqlite:///src/db.sqlite3` |
| `CSRF_TRUSTED_ORIGINS`   | Comma-separated trusted origins | For POST requests | —                          |
| `DJANGO_SETTINGS_MODULE` | Django settings module          | No                | `config.settings`          |
| `PORT`                   | Web server port                 | No                | `8000`                     |
| `TIME_ZONE`              | IANA timezone                   | No                | `UTC`                      |
| `EMAIL_BACKEND`          | Email backend                   | No                | `smtp.EmailBackend`        |

### Procfile

Create a `Procfile` in the project root:

```procfile
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --chdir src
release: python src/manage.py migrate --noinput
```

- `web` — starts Gunicorn on the port provided by the platform.
- `release` — runs database migrations once before each deploy.

### Static Files with WhiteNoise

This project uses [WhiteNoise](https://whitenoise.readthedocs.io/) to serve static files directly from the app container. No separate web server is needed for static files on PaaS platforms.

The middleware is already wired in `src/config/settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # right after SecurityMiddleware
    # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Run `collectstatic` during every deploy:

```bash
python src/manage.py collectstatic --noinput
```

### Security Settings for Production

Ensure these are set in your environment:

```env
DEBUG=False
SECRET_KEY=<long-random-string>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

______________________________________________________________________

## Dokploy (Self-hosted PaaS)

[Dokploy](https://dokploy.com) is an open-source Heroku alternative. It deploys via Docker and routes traffic through Traefik with automatic TLS.

### Prerequisites

- A Dokploy instance (self-hosted on a VPS)
- Your project pushed to a Git repository

### Configuration

1. **Dockerfile** — the existing `Docker/Dockerfile` is ready. It performs a two-stage build with `uv` and serves via Gunicorn (`--chdir src`). In Dokploy's build settings, set the Dockerfile path to `Docker/Dockerfile`.

1. **Environment Variables** — set these in the Dokploy dashboard (Services → your service → Variables):

   ```env
   DJANGO_SETTINGS_MODULE=config.settings
   PYTHONPATH=/app/src
   SECRET_KEY=<your-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=.dokploy.app,yourdomain.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com
   DATABASE_URL=postgres://user:password@db:5432/dbname
   PORT=8000
   ```

1. **PostgreSQL** — add a PostgreSQL service from Dokploy's service catalog, or define it in a `docker-compose.yml` sidecar:

   ```yaml
   services:
     db:
       image: postgres:17-alpine
       environment:
         POSTGRES_DB: mydb
         POSTGRES_USER: myuser
         POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data

   volumes:
     postgres_data:
   ```

1. **Domain & TLS** — configure your domain in Dokploy's Traefik settings. Traefik automatically provisions Let's Encrypt certificates.

### Deployment Workflow

1. Push code to your Git repository.
1. Dokploy detects the push (via webhook) and rebuilds the Docker image.
1. Traefik routes traffic to the new container.
1. Run migrations: `docker compose exec web python src/manage.py migrate`

______________________________________________________________________

## Railway (Managed PaaS)

[Railway](https://railway.app) uses Nixpacks to auto-detect your project and build it without a Dockerfile.

### Configuration

1. **Connect Repository** — link your Git repository in the Railway dashboard.

1. **Procfile** — Railway reads the `Procfile` at the project root to determine the start command. The provided `Procfile` is sufficient.

1. **PostgreSQL** — add a PostgreSQL plugin from Railway's dashboard. It automatically injects a `DATABASE_URL` environment variable.

1. **Environment Variables** — set in the Variables tab:

   ```env
   SECRET_KEY=<your-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=.up.railway.app,yourdomain.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com
   DJANGO_SETTINGS_MODULE=config.settings
   ```

### Static Files

Railway runs `collectstatic` automatically when detected. Ensure WhiteNoise is configured as described in [Shared Configuration](#shared-configuration).

### Deployment

Push to your connected branch — Railway automatically builds and deploys.

______________________________________________________________________

## Fly.io (Managed PaaS)

[Fly.io](https://fly.io) deploys Docker containers close to your users.

### Initial Setup

```bash
# Install flyctl and log in
fly auth login

# Initialize the app (creates fly.toml)
fly launch --no-deploy

# Create and attach PostgreSQL
fly postgres create
fly postgres attach <pg-name>

# Set secrets (not in fly.toml)
fly secrets set SECRET_KEY=<your-secret-key>
fly secrets set DEBUG=False
fly secrets set ALLOWED_HOSTS=.fly.dev,yourdomain.com
fly secrets set CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### fly.toml

After running `fly launch`, edit the generated `fly.toml`:

```toml
app = "your-app-name"
primary_region = "ams"

[build]
  dockerfile = "Docker/Dockerfile"

[env]
  DJANGO_SETTINGS_MODULE = "config.settings"
  PYTHONPATH = "/app/src"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "off"
  auto_start_machines = true
  min_machines_running = 1

[deploy]
  release_command = "python src/manage.py migrate --noinput"
```

### Deployment

```bash
fly deploy
```

This builds the Docker image, runs migrations (via `release_command`), then starts the app.

### Management Commands

```bash
# One-off commands
fly ssh console -C "python src/manage.py createsuperuser"

# View logs
fly logs
```

______________________________________________________________________

## Hetzner VPS (Docker Compose + Caddy)

Deploy on a Hetzner CX-series VPS using Docker Compose with Caddy as a reverse proxy.

### Server Setup

```bash
# SSH into your Hetzner VPS (Ubuntu 24.04)
ssh root@<your-vps-ip>

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Configure Hetzner Cloud Firewall (via web console):
# Allow: 22 (SSH), 80 (HTTP), 443 (HTTPS)
# Deny: all other inbound
```

### Project Structure on Server

```
/opt/myproject/
  .env               # Production secrets (never committed)
  docker-compose.yml
  Caddyfile
  app/               # Your Django project
    Docker/
    src/
    pyproject.toml
    ...
```

### Environment File (`.env`)

```env
# Django
SECRET_KEY=<your-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DJANGO_SETTINGS_MODULE=config.settings

# PostgreSQL
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=<strong-db-password>

# Gunicorn
PORT=8000
```

### Docker Compose

```yaml
services:
  web:
    build:
      context: ./app
      dockerfile: Docker/Dockerfile
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    expose:
      - "8000"
    volumes:
      - static_data:/app/src/staticfiles
      - media_data:/app/src/media

  db:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  caddy:
    image: caddy:2
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
      - static_data:/staticfiles
      - media_data:/media
    depends_on:
      - web

volumes:
  postgres_data:
  static_data:
  media_data:
  caddy_data:
  caddy_config:
```

### Caddyfile

```caddy
yourdomain.com, www.yourdomain.com {
    encode gzip zstd

    # Static files (collected by Django)
    handle_path /static/* {
        root * /staticfiles
        file_server
    }

    # Media files (user uploads)
    handle_path /media/* {
        root * /media
        file_server
    }

    # Proxy everything else to Django
    reverse_proxy web:8000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
    }

    # Security headers
    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

### Deployment

```bash
# Clone or copy your project
git clone <your-repo> /opt/myproject/app
cd /opt/myproject

# Create .env with production values
# (manually or via a secrets manager)

# Start services
docker compose up -d

# Run migrations and collect static files
docker compose run --rm web python src/manage.py migrate --noinput
docker compose run --rm web python src/manage.py collectstatic --noinput

# Restart web to pick up static files
docker compose restart web

# Verify
docker compose ps
docker compose logs web
```

### Backups

```bash
# Backup PostgreSQL
docker compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%Y%m%d).sql

# Schedule via cron (daily)
0 2 * * * cd /opt/myproject && docker compose exec -T db pg_dump -U myuser mydb > /backups/db_$(date +\%Y\%m\%d).sql
```

______________________________________________________________________

## DigitalOcean (Docker Compose + Caddy)

The DigitalOcean Droplet setup is nearly identical to Hetzner. Key differences are noted below.

### Managed PostgreSQL (Recommended)

Instead of running PostgreSQL in a container, use DigitalOcean's managed database:

1. Create a Managed PostgreSQL cluster in the DO control panel.

1. Add your Droplet's IP as a trusted source.

1. Use the provided connection string:

   ```env
   DATABASE_URL=postgres://user:password@host:port/dbname?sslmode=require
   ```

1. Remove the `db` service from `docker-compose.yml`.

### DO Spaces for Media Files

For user-uploaded media, use DigitalOcean Spaces (S3-compatible):

```bash
uv add django-storages boto3
```

```python
# src/config/settings.py
INSTALLED_APPS += ['storages']

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
```

### DO App Platform (Alternative)

For a fully managed experience:

| Setting           | Value                                                                                              |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| **Source**        | GitHub repository                                                                                  |
| **Build Command** | `uv sync --no-dev && python src/manage.py collectstatic --noinput && python src/manage.py migrate` |
| **Run Command**   | `gunicorn config.wsgi:application --bind 0.0.0.0:8080 --chdir src`                                 |
| **HTTP Port**     | `8080`                                                                                             |
| **Env Vars**      | `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `DATABASE_URL`                                       |
| **Database**      | Attach Managed PostgreSQL (injects `DATABASE_URL` automatically)                                   |

______________________________________________________________________

## Caddy Configuration Reference

Caddy is used for VPS deployments (Hetzner, DigitalOcean) as a reverse proxy with automatic HTTPS.

### Key Features

- **Automatic HTTPS** — Caddy obtains and renews Let's Encrypt certificates for you. No manual certificate management.
- **Reverse Proxy** — forwards requests to Gunicorn running in the `web` container.
- **Static File Serving** — serves `collectstatic` output directly, offloading Django.
- **Security Headers** — HSTS, X-Content-Type-Options, X-Frame-Options.
- **HTTP/2 and HTTP/3** — supported out of the box.

### Minimal Caddyfile

```caddy
yourdomain.com {
    reverse_proxy web:8000
}
```

That is all you need for HTTPS + reverse proxy. Caddy automatically redirects HTTP to HTTPS.

### Full Production Caddyfile

See the [Hetzner VPS](#hetzner-vps-docker-compose--caddy) section for a complete annotated example with static/media file serving and security headers.

______________________________________________________________________

## Production Checklist

- [ ] `DEBUG=False` in production environment
- [ ] `SECRET_KEY` is a long, random string (`openssl rand -base64 48`)
- [ ] `ALLOWED_HOSTS` includes your domain(s)
- [ ] `CSRF_TRUSTED_ORIGINS` includes your HTTPS domain(s)
- [ ] `CSRF_COOKIE_SECURE=True` and `SESSION_COOKIE_SECURE=True`
- [ ] Static files are collected (`collectstatic --noinput` runs on deploy)
- [ ] WhiteNoise middleware is correctly positioned (after `SecurityMiddleware`)
- [ ] Database is backed up regularly
- [ ] Logging is configured (stdout for containerized environments)
- [ ] Health check endpoint (`/health/`) returns 200
- [ ] `python src/manage.py check --deploy` passes

______________________________________________________________________

## Troubleshooting

| Problem                     | Likely Cause                        | Fix                                             |
| --------------------------- | ----------------------------------- | ----------------------------------------------- |
| 400 Bad Request             | `ALLOWED_HOSTS` missing your domain | Add domain to `ALLOWED_HOSTS`                   |
| 403 Forbidden on POST       | `CSRF_TRUSTED_ORIGINS` not set      | Add `https://yourdomain.com`                    |
| Static files 404            | `collectstatic` not run             | Run `collectstatic --noinput`                   |
| Database connection refused | Wrong host/credentials              | Check `DATABASE_URL` or `POSTGRES_*` vars       |
| Caddy certificate error     | DNS not propagated                  | Verify DNS A record points to server IP         |
| Gunicorn won't start        | Missing `--chdir src`               | Ensure `--chdir src` is in the gunicorn command |

### Viewing Logs

```bash
# Dokploy / Docker
docker compose logs -f web

# Railway
railway logs

# Fly.io
fly logs

# Docker Compose (Hetzner / DO)
docker compose logs -f web caddy
docker compose logs -f db
```

______________________________________________________________________

## Appendix: Gunicorn Configuration

The project uses Gunicorn with these defaults:

- **Bind:** `0.0.0.0:$PORT` (port provided by the platform)
- **Workers:** 3 (adjust based on CPU cores: `2n+1`)
- **Chdir:** `src` (because the Django project lives under the `src/` directory)
- **WSGI app:** `config.wsgi:application`

To customize, modify the `Procfile` or the `CMD` in `Docker/Dockerfile`.
