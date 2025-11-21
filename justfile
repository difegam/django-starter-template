set dotenv-load := true
alias dj-rs := dj-runserver

# Available recipes
@_:
    echo "Available recipes:"
    just --list

# Run the application locally
[group("django")]
run:
    @echo "🚀 Starting the Django development server..."
    uv run python src/manage.py runserver

# Run linter and formatter
[group("qa")]
lint:
    uv run ruff check --fix
    uv run ruff format

# Run pre-commit hooks on all files
[group('qa')]
check:
    @echo "Running pre-commit hooks on all files"
    @uv run pre-commit run --all-files

# Run Tests
[group('qa')]
test:
    echo "🧪 Testing app...! "
    @uv run pytest -vv --tb=short -s tests/

# Create a requirements.txt from pyproject.toml
[group('development')]
export-requirements:
    @echo "Exporting requirements"
    uv pip compile pyproject.toml -o requirements.txt

# Build docker images
[group('docker')]
build *ARGS:
    @echo "Building docker images"

# 🐳 “Dive” is a tool that helps you explore a Docker image, examine its layers, and find ways to reduce its size.
[group('docker')]
dive *ARGS:
    @echo "Exploring docker image"
    @docker run -ti --rm  -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive {{ARGS}}

# Ensure project virtualenv is up to date
[group("development")]
install:
    @echo "📦 Installing the application for development"
    uv sync --all-groups
    uv run pre-commit install
    @echo "\n✅ Setup complete, ready to code 🚀"

# Update dependencies
[group("development")]
update:
    uv sync --all-groups

# Remove temporary files
[group("development")]
clean:
    rm -rf .venv .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
    find . -type d -name "__pycache__" -exec rm -r {} +

# Recreate project virtualenv from nothing
[group("development")]
fresh: clean install
    @echo "✅ Fresh setup complete, ready to code 🚀"

# Django specific commands
# Run Django development server
[group("django")]
dj-runserver:
    uv run python src/manage.py runserver

# Apply database migrations
[group("django")]
dj-migrate: _makemigrations
    uv run python src/manage.py migrate

# Create database migrations
_makemigrations:
    uv run python src/manage.py makemigrations

[group("django")]
[doc("Run Django migrations")]
dj-superuser:
    uv run python src/manage.py createsuperuser

[group("django")]
[doc("Start Django shell")]
dj-shell:
    uv run python src/manage.py shell

[group("django")]
[doc("Run Django deploy check")]
dj-check:
    uv run python src/manage.py check --deploy

# Collect static files
[group("django")]
dj-collectstatic:
    uv run python src/manage.py collectstatic --noinput

# New app creation
[group("django")]
[working-directory("src")]
@new-app NAME:
    # Use module invocation to avoid missing django-admin script issues
    uv run python -m django startapp {{NAME}}
    mkdir -p {{NAME}}/templates/{{NAME}} {{NAME}}/static/{{NAME}}
    echo "Remember to add {{BLUE}}'{{NAME}}'{{NORMAL}} to CUSTOM_APPS in {{BLUE}}src/config/settings.py{{NORMAL}}"
