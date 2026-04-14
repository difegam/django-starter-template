# =============================================================================
# Stage 1: Build
# =============================================================================
FROM python:3.13-slim AS build

SHELL ["sh", "-exc"]

ENV PYTHON_VERSION=python3.13 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# Install build dependencies
RUN apt-get update -qy && apt-get upgrade -y && \
    apt-get install -qyy --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables for uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=${PYTHON_VERSION} \
    UV_PROJECT_ENVIRONMENT=/app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (without the project itself)
RUN --mount=type=cache,target=/root/.cache \
    uv sync \
    --locked \
    --no-install-project

# Copy the full source code
COPY . /app
WORKDIR /app

# Install the project (production deps only, no editable install)
RUN --mount=type=cache,target=/root/.cache \
    uv sync \
    --locked \
    --no-dev \
    --no-editable

# Collect static files during build
ENV DJANGO_SETTINGS_MODULE=config.settings
RUN SECRET_KEY=build-placeholder \
    DEBUG=False \
    DATABASE_URL=sqlite:///tmp/build.sqlite3 \
    python src/manage.py collectstatic --noinput 2>/dev/null || true

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.13-slim AS runtime

SHELL ["sh", "-exc"]

# Install minimal runtime dependencies
RUN apt-get update -qy && apt-get upgrade -y && \
    apt-get install -qyy --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PATH="/app/bin:$PATH" \
    PYTHONPATH="/app/src" \
    DJANGO_SETTINGS_MODULE=config.settings \
    APP_USER=appuser \
    APP_GROUP=appuser \
    APP_ID=1001

# Create non-root user
RUN groupadd -g ${APP_ID} ${APP_GROUP} && \
    useradd -u ${APP_ID} -g ${APP_GROUP} \
    -m -d /home/${APP_USER} \
    -s /bin/bash ${APP_USER}

# Copy the application from the build stage
COPY --from=build --chown=${APP_USER}:${APP_GROUP} /app /app

# Set the working directory
WORKDIR /app

# Switch to non-root user
USER ${APP_USER}

# Expose Django default port
EXPOSE 8000

# Run the application with gunicorn
ENTRYPOINT ["python", "-m", "gunicorn", "config.wsgi:application"]
CMD ["--bind", "0.0.0.0:8000", "--workers", "3", "--chdir", "src"]
