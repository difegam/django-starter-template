"""Tests for web.views."""

from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

# ---------------------------------------------------------------------------
# Home view
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_home_status_code(client: Client) -> None:
    """GET / returns HTTP 200 OK."""
    url = reverse('web:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_home_template_used(client: Client) -> None:
    """GET / renders the correct template."""
    url = reverse('web:home')
    response = client.get(url)
    assert 'index.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_home_accessible_to_anonymous_users(client: Client) -> None:
    """The home page does not require authentication."""
    url = reverse('web:home')
    response = client.get(url)
    # A redirect would indicate the view requires login; 200 means it is public.
    assert response.status_code == HTTPStatus.OK
