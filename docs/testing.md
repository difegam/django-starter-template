# Testing

This project uses **[pytest](https://docs.pytest.org/)** with **[pytest-django](https://pytest-django.readthedocs.io/)** for testing. Tests live in the top-level `tests/` directory, organized by app.

______________________________________________________________________

## Running tests

```bash
# Run all tests
just test

# Or without Just
uv run pytest -vv tests/

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run a specific file
uv run pytest tests/web/test_home.py -vv

# Run a specific test
uv run pytest tests/web/test_home.py::test_home_view_returns_200 -vv
```

______________________________________________________________________

## Test structure

```
tests/
├── conftest.py          # Shared fixtures (user, admin_user, authenticated_client)
├── users/
│   └── test_models.py   # CustomUser model tests
└── web/
    ├── test_home.py     # Home view tests
    └── test_views.py    # Additional view tests
```

______________________________________________________________________

## Shared fixtures (`tests/conftest.py`)

Reusable fixtures available in all tests:

```python
@pytest.fixture
def user(db):
    """A regular (non-staff) CustomUser."""
    return CustomUser.objects.create_user(
        username='testuser',
        email='user@example.com',
        password='ThisIsATestPassword123',
    )


@pytest.fixture
def admin_user(db):
    """A superuser (staff + admin)."""
    return CustomUser.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPassword123',
    )


@pytest.fixture
def authenticated_client(client, user):
    """A test client pre-authenticated as the test user."""
    client.force_login(user)
    return client
```

Use these fixtures by name in your test functions — pytest auto-discovers them.

______________________________________________________________________

## Writing model tests

Model tests verify field values, methods, constraints, and the `__str__` representation.

```python
# tests/users/test_models.py
import pytest
from users.models import CustomUser


@pytest.mark.django_db
def test_custom_user_str_returns_email(user: CustomUser) -> None:
    """str(user) should return the email address."""
    assert str(user) == user.email


@pytest.mark.django_db
def test_custom_user_creation(user: CustomUser) -> None:
    """A newly created user should have the expected field values."""
    assert user.email == 'user@example.com'
    assert user.username == 'testuser'
    assert user.is_active is True
    assert user.is_staff is False


@pytest.mark.django_db
def test_custom_user_password_is_hashed(user: CustomUser) -> None:
    """Passwords must never be stored in plain text."""
    assert user.check_password('ThisIsATestPassword123') is True
    assert 'ThisIsATestPassword123' not in user.password
```

**Key points:**

- Use `@pytest.mark.django_db` to enable database access
- Each test runs in its own transaction, rolled back automatically
- Use the `user` or `admin_user` fixtures for existing users

______________________________________________________________________

## Writing view tests

View tests verify HTTP status codes, templates, redirects, and authentication requirements.

```python
# tests/web/test_home.py
from http import HTTPStatus
from typing import cast

import pytest
from django.test import Client
from django.urls import reverse
from django.http import HttpResponse


@pytest.mark.django_db
def test_home_view_returns_200(client: Client) -> None:
    """GET / returns HTTP 200 OK."""
    url = reverse('web:home')
    response = cast(HttpResponse, client.get(url))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_home_view_uses_index_template(client: Client) -> None:
    """GET / renders the index.html template."""
    url = reverse('web:home')
    response = cast(HttpResponse, client.get(url))
    template_names = [t.name for t in response.templates]
    assert 'index.html' in template_names


@pytest.mark.django_db
def test_home_view_accessible_without_authentication(client: Client) -> None:
    """The home view does not require login."""
    url = reverse('web:home')
    response = cast(HttpResponse, client.get(url))
    assert response.status_code != HTTPStatus.FOUND  # no redirect
    assert response.status_code == HTTPStatus.OK
```

**Key points:**

- Use `django.urls.reverse()` to generate URLs by name — never hardcode paths
- Use the `client` fixture for HTTP requests
- Use `cast(HttpResponse, ...)` for proper typing
- Test anonymous access, authenticated access, and redirects separately

### Testing protected views

```python
@pytest.mark.django_db
def test_protected_view_requires_login(client: Client) -> None:
    """Unauthenticated users are redirected to login."""
    url = reverse('some-protected-view')
    response = cast(HttpResponse, client.get(url))
    assert response.status_code == HTTPStatus.FOUND  # 302 redirect
    assert '/accounts/login/' in response.url


@pytest.mark.django_db
def test_protected_view_accessible_when_authenticated(
    authenticated_client: Client,
) -> None:
    """Authenticated users can access the protected view."""
    url = reverse('some-protected-view')
    response = cast(HttpResponse, authenticated_client.get(url))
    assert response.status_code == HTTPStatus.OK
```

______________________________________________________________________

## Writing form tests

Form tests verify validation, cleaning, and error handling.

```python
# tests/web/test_forms.py
import pytest
from web.forms import ContactForm


def test_contact_form_valid_data() -> None:
    """A valid form should pass validation."""
    form = ContactForm(
        data={
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Hello!',
        }
    )
    assert form.is_valid() is True


def test_contact_form_missing_required_field() -> None:
    """A form with missing fields should fail validation."""
    form = ContactForm(
        data={
            'name': '',
            'email': 'test@example.com',
            'message': 'Hello!',
        }
    )
    assert form.is_valid() is False
    assert 'name' in form.errors


def test_contact_form_invalid_email() -> None:
    """An invalid email should fail validation."""
    form = ContactForm(
        data={
            'name': 'Test User',
            'email': 'not-an-email',
            'message': 'Hello!',
        }
    )
    assert form.is_valid() is False
    assert 'email' in form.errors
```

**Key points:**

- Form tests don't need `@pytest.mark.django_db` unless the form touches the database
- Test both valid and invalid data
- Assert specific error fields, not just "form is invalid"

______________________________________________________________________

## pytest-django markers

| Marker                                     | Purpose                                                                     |
| ------------------------------------------ | --------------------------------------------------------------------------- |
| `@pytest.mark.django_db`                   | Grants database access. Each test runs in a transaction                     |
| `@pytest.mark.django_db(transaction=True)` | Grants database access with transaction isolation (slower, use when needed) |
| `@pytest.mark.slow`                        | Custom marker for slow tests (run selectively)                              |

______________________________________________________________________

## Code coverage

Coverage reporting is available via `pytest-cov` (already in dev dependencies):

```bash
# Terminal report
uv run pytest --cov=src

# HTML report (opens in browser)
uv run pytest --cov=src --cov-report=html
# Then open htmlcov/index.html

# XML report (for CI)
uv run pytest --cov=src --cov-report=xml
```

Coverage thresholds are not enforced by default. To add a minimum threshold, add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = '--cov=src --cov-report=term-missing --cov-fail-under=80'
```

______________________________________________________________________

## GitHub Actions CI

The project includes a CI workflow in `.github/workflows/ci.yml` that runs on every push and pull request:

### Lint job

- Installs dependencies with `uv sync --locked --all-groups`
- Runs `ruff check src` (linting)
- Runs `ruff format --check` (formatting)
- Runs `ty check` (type checking)
- Runs `prek run --all-files` (pre-commit hooks)

### Test job

- Starts a PostgreSQL service container
- Installs dependencies
- Runs `pytest -vv --tb=short -s tests/ --cov=src --cov-report=xml`
- Uploads coverage to Codecov (optional)

### Locally replicating CI

```bash
# Simulate the lint job
just lint
just ty
uv run prek run --all-files

# Simulate the test job (with Postgres)
DATABASE_URL=postgres://user:pass@localhost:5432/test_db uv run pytest -vv tests/
```

______________________________________________________________________

## Best practices

1. **One assertion per test** — each test should verify exactly one behavior
1. **Descriptive test names** — `test_custom_user_str_returns_email` is better than `test_str`
1. **Use fixtures** — avoid duplicating object creation across tests
1. **Use `reverse()`** — never hardcode URLs; use named routes
1. **Mark DB tests** — use `@pytest.mark.django_db` only when you need database access
1. **Test edge cases** — invalid input, empty data, unauthorized access
1. **Keep tests fast** — avoid external API calls; use mocks when necessary

______________________________________________________________________

## Further reading

- [pytest-django documentation](https://pytest-django.readthedocs.io/)
- [Custom User Model](users.md) — testing patterns for user extensions
- [Settings & Environment](settings.md) — database and environment configuration
