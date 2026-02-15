---
description:
  This file describes the tech stack and dependency rules for the project.
applyTo: 'pyproject.toml,package.json,justfile,ruff.toml,pytest.ini,tailwind.config.js,postcss.config.js'
---

# Tech Stack and Dependency Rules

Use these rules when adding or updating project dependencies and tooling.

## Backend stack baseline

- **Python**: `3.13+` (Django 6.0 supports Python 3.12, 3.13, and 3.14)
- **Django**: `6.0.0+`
  - Django 6.0 changes: `DEFAULT_AUTO_FIELD` defaults to `BigAutoField`, email
    API keyword arguments required
  - Python 3.10 and 3.11 support ends with Django 5.2.x series
- **django-allauth**: `65+` for authentication, registration, and social account
  management
- **django-htmx**: `1.27+` for HTMX integration middleware and request helpers
- **django-cotton**: `2.6+` for component-based template design
- **django-environ**: `0.12+` for 12-factor app environment configuration
- **whitenoise**: `6.8+` for static file serving in production
- **psycopg**: `3.2+` with binary drivers for PostgreSQL support
- **gunicorn**: `23+` as production WSGI server

## Frontend stack baseline

- **Tailwind CSS**: `4.0+` (major version upgrade from v3)
  - Uses `@import "tailwindcss"` instead of `@tailwind` directives
  - Requires modern browsers: Safari 16.4+, Chrome 111+, Firefox 128+
  - Depends on modern CSS features like `@property` and `color-mix()`
  - Migration tool: `npx @tailwindcss/upgrade` (requires Node.js 20+)
- **daisyUI**: `5.5+` for semantic component classes built on Tailwind
- **Alpine.js**: Latest stable for lightweight reactive JavaScript
- **HTMX**: `1.9+` or `2.0+` for server-driven interactivity (loaded via CDN or
  npm)

## Development and quality stack baseline

- **ruff**: `0.14+` for fast linting and formatting (Rust-based, 10-100x faster
  than Flake8/Black)
- **ty**: `0.0.17+` for lightweight type checking (preferred for routine checks)
- **mypy**: `1.0+` with `django-stubs` `5.2.7+` for strict static typing
  (configure in `mypy.ini`)
- **pytest**: `8.4+` as testing framework
- **pytest-django**: `4.11+` for Django-specific test features
- **pytest-cov**: `7.0+` for coverage reporting
- **pre-commit**: `4.3+` for git hook management
- **django-debug-toolbar**: `6.0+` for development debugging (dev only)

## Security tooling baseline

- **bandit**: For security vulnerability scanning
- **detect-secrets**: For secret detection (maintain `.secrets.baseline`)
- **pip-audit**: For dependency vulnerability auditing via `uv` integration

## Dependency management rules

### Version pinning strategy

- Use `>=` with minor version for framework dependencies (e.g., `django>=6.0.0`)
- Pin exact major versions for breaking-change-prone tools (e.g.,
  `tailwindcss": "^4.0.0`)
- Review upstream changelogs before major version upgrades

### Update workflow

1. Check Context7 or official docs for breaking changes and migration guides
2. Update `pyproject.toml` or `package.json` with new version constraints
3. Run `uv sync` or `npm install` to update lockfiles
4. Update related configuration files (`ruff.toml`, `pytest.ini`,
   `tailwind.config.js`)
5. Run full validation: `just check` + `just test`
6. Update documentation and instruction files to reflect version changes
7. Commit with clear notes on what changed and why

### Compatibility matrix awareness

- Django 6.0 requires Python 3.12+
- Tailwind CSS v4 requires Node.js 20+ and modern browsers
- Keep `django-stubs` version aligned with Django version
- Verify django-allauth, django-htmx, django-cotton compatibility with Django
  version

### Adding new dependencies

- Justify the addition: what problem does it solve that existing tools don't?
- Check source reputation and maintenance status (use Context7 library search)
- Prefer well-documented, actively maintained packages with high benchmark
  scores
- Add to appropriate group in `pyproject.toml`: `dependencies` (runtime) or
  `dev` (development)
- Document integration patterns in relevant instruction files
- Update `justfile` recipes if new commands are needed

### Removing dependencies

- Verify no code depends on the package (use grep/semantic search)
- Remove from `pyproject.toml` or `package.json`
- Remove related configuration files or sections
- Run `uv sync --inexact` or `npm prune`
- Update documentation that referenced the removed dependency

## Browser and runtime target awareness

### Python runtime

- Target: Python 3.13+ (latest stable)
- Type hints: required on all new/changed functions
- Syntax: modern Python features allowed (match statements, structural pattern
  matching, etc.)

### Browser targets (Tailwind CSS v4)

- Safari 16.4+
- Chrome 111+
- Firefox 128+
- For older browser support, stay on Tailwind CSS v3.4

### Node.js runtime

- Minimum: Node.js 20+ (required for Tailwind CSS v4 tooling)
- Tooling only (not for production runtime)

## Critical update triggers

Update this instruction file when:

- Django, Tailwind CSS, or other core frameworks release major versions
- Python version requirements change
- Breaking changes occur in ruff, pytest, or type checking tools
- New dependencies are added to the baseline stack
- Security advisories require version bumps or replacements
