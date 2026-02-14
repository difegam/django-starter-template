set dotenv-load := true

# List available recipes
[private]
default:
    @just --list

[doc("Run the application locally")]
[group("django")]
serve:
    @echo "🚀 Starting the Django development server..."
    uv run python src/manage.py runserver

[doc('Run linter and formatter')]
[group("qa")]
lint:
    uv run ruff check --fix
    uv run ruff format

[doc('Run type checks with ty')]
[group('qa')]
ty:
    @echo 'Running ty type checks'
    @uv run ty check

[doc('Run type checks and pre-commit hooks')]
[group('qa')]
check: lint ty
    @echo 'Running pre-commit hooks on all files'
    @uv run pre-commit run --all-files

[doc('Run tests with pytest')]
[group('qa')]
test:
    echo "🧪 Testing app...! "
    @uv run pytest -vv --tb=short -s tests/

[doc('Create a requirements.txt from pyproject.toml')]
[group('development')]
export-reqs:
    @echo "Exporting requirements"
    @uv pip compile pyproject.toml -o requirements.txt

[doc('Install project dependencies and setup pre-commit hooks')]
[group('development')]
init:
    @echo '📦 Installing the application for development'
    @uv sync --all-groups
    @uv run pre-commit install
    @echo '✅ Setup complete, ready to code 🚀'

# Update dependencies
[group("development")]
update:
    @uv sync --all-groups

# Remove temporary files
[group("development")]
clean:
    rm -rf .venv .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
    find . -type d -name "__pycache__" -exec rm -r {} +

# Recreate project virtualenv from nothing
[group("development")]
fresh: clean init
    @echo "✅ Fresh setup complete, ready to code 🚀"

# Django specific commands

[doc("Apply database migrations")]
[group("django")]
migrate: makemigrations
    @uv run python src/manage.py migrate

[doc("Create new Django migrations based on model changes")]
[private]
makemigrations:
    @uv run python src/manage.py makemigrations

[doc("Create a Django superuser")]
[group("django")]
add-superuser:
    @uv run python src/manage.py createsuperuser

[doc("Start Django shell")]
[group("django")]
shell:
    @uv run python src/manage.py shell

[doc("Run Django deploy check")]
[group("django")]
deploy-check:
    @uv run python src/manage.py check --deploy

[doc("Collect static files")]
[group("django")]
collectstatic:
    @uv run python src/manage.py collectstatic --noinput

[doc("Create a new Django app with the given NAME")]
[group("django")]
[working-directory("src")]
new NAME:
    # Use module invocation to avoid missing django-admin script issues
    @uv run python -m django startapp {{ NAME }}
    mkdir -p {{ NAME }}/templates/{{ NAME }} {{ NAME }}/static/{{ NAME }}
    echo "Remember to add {{ BLUE }}'{{ NAME }}'{{ NORMAL }} to CUSTOM_APPS in {{ BLUE }}src/config/settings.py{{ NORMAL }}"
