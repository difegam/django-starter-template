"""Tests for users.models."""

import pytest

from users.models import CustomUser

# ---------------------------------------------------------------------------
# CustomUser model
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_custom_user_str_returns_email(user: CustomUser) -> None:
    """str(user) should return the user's email address, not the username."""
    assert str(user) == user.email


@pytest.mark.django_db
def test_custom_user_creation(user: CustomUser) -> None:
    """A newly created user should have the expected field values."""
    assert user.email == 'user@example.com'
    assert user.username == 'testuser'
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_custom_user_password_is_hashed(user: CustomUser) -> None:
    """Passwords must never be stored in plain text."""
    # Django's check_password() verifies against the stored hash.
    assert user.check_password('supersecretpassword123') is True
    # The raw password must not appear in the stored hash string.
    assert 'supersecretpassword123' not in user.password
