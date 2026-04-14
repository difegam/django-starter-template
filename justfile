set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set dotenv-load := true

# List available recipes
[private]
default:
    @just --list --list-submodules

mod docker "Docker/docker.just"
mod django "django.just"

[doc('Run linter and formatter')]
[group("qa")]
lint:
    uv run ruff check src --fix --show-fixes
    uv run ruff format

[doc('Run type checks with ty')]
[group('qa')]
ty:
    @echo 'Running ty type checks'
    @uv run ty check

[doc('Run type checks and pre-commit-stage hooks')]
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
    @uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push
    @echo '✅ Setup complete, ready to code 🚀'

[doc('Update project dependencies')]
[group("development")]
update:
    @uv lock --upgrade && uv sync --all-groups
    @echo '✅ Dependencies updated successfully 🚀'

[doc('Remove temporary files')]
[group("development")]
clean:
    rm -rf .venv .pytest_cache .mypy_cache .ty_cache .ruff_cache .coverage htmlcov
    find . -type d -name "__pycache__" -exec rm -r {} +

[doc('Recreate project virtualenv from scratch')]
[group("development")]
fresh: clean init
    @uv run pre-commit clean
    @echo "✅ Fresh setup complete, ready to code 🚀"
