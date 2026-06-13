# Contributing

Guidelines for maintaining dependencies, updating hooks, and contributing to this template.

## Dependency management

### Adding a dependency

```bash
# Add a core dependency
uv add <package-name>

# Add a dev dependency
uv add --group dev <package-name>
```

Then update the lockfile:

```bash
uv lock
```

### Updating all dependencies

```bash
# Update all packages to latest compatible versions
just update

# Or without Just
uv lock --upgrade && uv sync --all-groups
```

### Removing a dependency

```bash
uv remove <package-name>
uv lock
```

### Exporting requirements.txt

If you need a `requirements.txt` (for platforms that don't support `pyproject.toml`):

```bash
just export-reqs
# Or: uv pip compile pyproject.toml -o requirements.txt
```

## Pre-commit hooks (prek)

This project uses **[prek](https://github.com/dferguson/prek)** for managing Git hooks. Hooks run automatically on commit and push.

### What hooks run

| Stage             | Hooks                                                                                           |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| **Commit**        | pre-commit-hooks, djlint, pyupgrade, ruff (lint + format), mdformat, codespell, shellcheck      |
| **Push / manual** | ty (type check), vulture (unused code), bandit (security), uv-secure (dependency vulns), pytest |

The exact hook list lives in [`.pre-commit-config.yaml`](../.pre-commit-config.yaml). Update this table whenever hooks are added or removed.

### Installing hooks

```bash
just init
# Or: uv run prek install --prepare-hooks --hook-type pre-commit --hook-type pre-push
```

### Updating hook revisions

Hook versions are pinned in `.pre-commit-config.yaml`. To update them:

```bash
just hooks-update
# Or: uv run prek auto-update --cooldown-days 7
```

### Running hooks manually

```bash
# Run all hooks on all files
uv run prek run --all-files

# Run only commit-stage hooks
uv run prek run --all-files --hook-type pre-commit
```

## Code style

### Python

The project enforces consistent style via **Ruff** (configured in `ruff.toml`):

- **Quotes**: single quotes
- **Line length**: 120 characters
- **Import sorting**: automatic
- **Python target**: 3.13+

Run the linter and formatter:

```bash
just lint
# Or: uv run ruff check src --fix --show-fixes && uv run ruff format
```

### Type hints

All new Python code should include type annotations. The project uses **ty** with django-stubs for type checking:

```bash
just ty
# Or: uv run ty check
```

### Templates

Django templates are linted by **djlint** (Django profile). Template files must follow HTML conventions with proper indentation.

### Documentation

- Use sentence case for headings.
- Prefer short sections with concrete commands over long prose.
- Do not use decorative horizontal divider lines; headings provide structure.
- Keep README as the high-level entry point and link to `docs/` for detail.

### Commit messages

The project follows [Conventional Commits](https://www.conventionalcommits.org/) conventions:

| Prefix      | When to use                                |
| ----------- | ------------------------------------------ |
| `feat:`     | New feature or functionality               |
| `fix:`      | Bug fix                                    |
| `docs:`     | Documentation changes                      |
| `test:`     | Adding or updating tests                   |
| `chore:`    | Maintenance, dependency updates            |
| `refactor:` | Code restructuring without behavior change |
| `ci:`       | CI/CD workflow changes                     |
| `config:`   | Configuration changes                      |
| `perf:`     | Performance improvements                   |
| `style:`    | Code style (formatting, whitespace)        |
| `build:`    | Build system or external dependencies      |

Examples:

```
feat: add password reset view
fix: handle empty form submission
docs: update deployment guide with Cloudflare steps
test: add form validation tests
chore: update Django to 6.0.5
```

## Pull request workflow

### Before opening a PR

1. Run all quality checks:

```bash
just check
```

2. Run the test suite:

```bash
just test
```

3. If either fails, fix the issues before opening the PR.

### PR checklist

- [ ] `just check` passes (lint + type check + hooks)
- [ ] `just test` passes
- [ ] New features have tests
- [ ] Documentation is updated if behavior changes
- [ ] No secrets or credentials are committed
- [ ] Migration files are included if models change
- [ ] Commit messages follow conventional commit format

### PR description

Include in your PR description:

1. What the change does
1. Why the change is needed
1. How to test it manually
1. Any environment variable changes or migrations

## Running quality checks

| What          | Command            |
| ------------- | ------------------ |
| Lint + format | `just lint`        |
| Type check    | `just ty`          |
| All checks    | `just check`       |
| Tests         | `just test`        |
| Docs format   | `just docs-format` |
| Docs links    | `just docs-check`  |
| Full reset    | `just fresh`       |

## Common tasks

### Creating a new Django app

```bash
just django new <app-name>
```

This creates `src/<app-name>/` with standard Django app files, templates, and static directories. Don't forget to add the app to `LOCAL_APPS` in `src/config/settings.py`.

### Running the development server

```bash
just django serve
```

### Running migrations

```bash
just django migrate
```

### Cleaning up

```bash
# Remove caches and virtual environment
just clean

# Full fresh start (clean + reinstall + clear prek cache)
just fresh
```

## Project conventions

- **`src/` layout**: all Django apps live under `src/`
- **Flat test directory**: tests mirror the `src/` structure in `tests/`
- **Shared fixtures**: reusable fixtures go in `tests/conftest.py`
- **Template overrides**: allauth template overrides go in `src/templates/account/`
- **Static assets**: project-wide static files in `src/static/`, app-specific in `src/<app>/static/<app>/`
- **Settings**: single file at `src/config/settings.py` (django-environ)

## Releasing and publishing Docker images

The release workflow is documented here from a contributor perspective. For operational details about the Docker publishing workflow, see [GitHub Actions: Publish Docker image](deployment.md#github-actions-publish-docker-image).

### Prerequisites

Set these GitHub repository secrets (Settings → Secrets and variables → Actions):

| Secret              | Value                                                                            |
| ------------------- | -------------------------------------------------------------------------------- |
| `DOCKER_IMAGE_NAME` | Your Docker Hub image, e.g. `youruser/your-app`                                  |
| `DOCKER_USERNAME`   | Docker Hub username                                                              |
| `DOCKER_PASSWORD`   | Docker Hub access token (create at hub.docker.com → Account Settings → Security) |

### Creating a release

```bash
# Tag and create a GitHub release (triggers the Docker image build)
git tag v1.0.0
git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0" --generate-notes
```

The workflow builds `Docker/Dockerfile`, tags the image, and pushes it to Docker Hub.

### Manual trigger

You can also trigger a build manually from the **Actions** tab in GitHub, optionally providing a custom tag. If no tag is provided, the image is tagged `manual`.

## Further reading

- [Quick Start](quickstart.md) — getting started
- [Settings & Environment](settings.md) — environment variables
- [User Model](users.md) — custom user setup
- [Authentication](authentication.md) — allauth and social logins
- [Testing](testing.md) — writing and running tests
- [Deployment](deployment.md) — Docker and production
