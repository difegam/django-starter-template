"""
Shared pytest fixtures available to all tests.

pytest-django automatically discovers this file and makes its fixtures
available without explicit imports in test modules.
"""

import pytest

from users.models import CustomUser


@pytest.fixture
def user(db: None) -> CustomUser:
    """Return a regular (non-staff) CustomUser saved to the test database.

    The ``db`` fixture argument grants database access for the duration of
    this fixture, which in turn grants it to any test that uses ``user``.

    Usage::

        def test_something(user: CustomUser) -> None:
            assert user.email == 'user@example.com'
    """
    return CustomUser.objects.create_user(
        username='testuser',
        email='user@example.com',
        password='ThisIsATestPassword123',  # noqa: S106
    )
