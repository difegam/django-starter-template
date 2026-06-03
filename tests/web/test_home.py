"""
Tests for web.views.home view.

This module demonstrates how to test Django views using pytest-django. It serves
as a template for testing other views in the project.

Key Testing Patterns:
  1. Use @pytest.mark.django_db to grant database access. Each test runs in its
     own transaction, which is automatically rolled back after the test
     completes, ensuring test isolation.
  2. Use the built-in pytest-django ``client`` fixture to make HTTP requests.
  3. Use django.urls.reverse() to generate URLs by their named route. This is
     safer than hardcoding URLs, as it automatically handles namespace routing
     (e.g., 'web:home' for the web app's home view).
  4. One assertion per test: Each test should verify exactly one behavior.
     This makes tests easier to understand, maintain, and debug.
  5. Use descriptive test names that clearly communicate what is being tested.

Test-Driven Development (TDD):
  These tests can be written BEFORE implementing the view. Simply run the tests
  (they will fail), then implement the view to make them pass. This ensures you
  implement exactly what is needed and nothing more.

Extending to Other Views:
  Copy the test structure from test_home_view_returns_200 and adapt for your
  new view. Then add app-specific assertions (e.g., context data, form presence).
"""

from http import HTTPStatus
from typing import TYPE_CHECKING, cast

import pytest
from django.test import Client
from django.urls import reverse

if TYPE_CHECKING:
    from django.http import HttpResponse


@pytest.mark.django_db
def test_home_view_returns_200(client: Client) -> None:
    """Verify that GET / returns HTTP 200 OK.

    This is the most basic test: the view should respond with a success
    status code for an unauthenticated user.
    """
    url = reverse('web:home')
    response = cast('HttpResponse', client.get(url))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_home_view_uses_index_template(client: Client) -> None:
    """Verify that GET / renders the index.html template.

    This test ensures the view is using the correct template file. The
    response.templates attribute is populated by Django's test client and
    contains a list of all templates rendered during the request.
    """
    url = reverse('web:home')
    response = cast('HttpResponse', client.get(url))
    template_names = [t.name for t in response.templates]
    assert 'index.html' in template_names


@pytest.mark.django_db
def test_home_view_accessible_without_authentication(client: Client) -> None:
    """Verify that the home view does not require login.

    Anonymous users should be able to access the home page. A redirect to the
    login page (HTTP 302) would indicate the view requires authentication. An
    HTTP 200 status code confirms the view is publicly accessible.
    """
    url = reverse('web:home')
    response = cast('HttpResponse', client.get(url))
    # No redirect means the view is public and accessible to everyone
    assert response.status_code != HTTPStatus.FOUND  # 302 redirect
    assert response.status_code == HTTPStatus.OK
