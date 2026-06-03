"""
Shared pytest fixtures available to all tests.

This conftest.py configures pytest-django for the project and provides reusable
fixtures across all test modules. pytest-django automatically discovers this
file and makes its fixtures available without explicit imports in test modules.

Key pytest-django concepts:
  - The ``db`` fixture grants database access for a test or fixture.
  - Each test wrapped with @pytest.mark.django_db runs in its own transaction,
    rolled back automatically after the test completes. This ensures test
    isolation and prevents side effects.
  - Fixtures defined here are shared across all test subdirectories
    (tests/users/, tests/web/, etc.).
  - The ``client`` and ``admin_user`` fixtures are provided by pytest-django
    and do not need to be defined here.

Settings Reference:
  - DJANGO_SETTINGS_MODULE is configured in pyproject.toml as 'config.settings'
  - AUTH_USER_MODEL is set to 'users.CustomUser' (custom user model)
  - Database defaults to SQLite at src/db.sqlite3, configurable via DATABASE_URL
"""

from collections.abc import Generator

import pytest
from django.test import Client

from users.models import CustomUser


@pytest.fixture
def user(db: None) -> CustomUser:
    """Create and return a regular (non-staff) CustomUser for testing."""
    return CustomUser.objects.create_user(
        username='testuser',
        email='user@example.com',
        password='ThisIsATestPassword123',  # noqa: S106
    )


@pytest.fixture
def admin_user(db: None) -> CustomUser:
    """Create and return a superuser (staff + admin) for testing."""
    return CustomUser.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPassword123',  # noqa: S106
    )


@pytest.fixture
def authenticated_client(client: Client, user: CustomUser) -> Generator[Client]:
    """Return a test client pre-authenticated as the test user.

    This fixture combines the pytest-django ``client`` and ``user`` fixtures
    to provide a client that is already logged in. Useful for testing
    protected views and user-specific functionality.
    """
    client.force_login(user)
    yield client
