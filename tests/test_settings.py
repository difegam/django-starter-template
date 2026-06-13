import importlib

import pytest

import config.settings as project_settings


@pytest.mark.parametrize(
    ('env_name', 'expected'),
    [
        ('SECURE_HSTS_INCLUDE_SUBDOMAINS', True),
        ('SECURE_HSTS_PRELOAD', True),
        ('SESSION_COOKIE_SECURE', True),
        ('CSRF_COOKIE_SECURE', True),
        ('SECURE_CONTENT_TYPE_NOSNIFF', False),
    ],
)
def test_boolean_security_settings_are_env_backed(
    monkeypatch: pytest.MonkeyPatch,
    env_name: str,
    expected: bool,
) -> None:
    monkeypatch.setenv(env_name, str(expected))

    reloaded_settings = importlib.reload(project_settings)

    assert getattr(reloaded_settings, env_name) is expected
    monkeypatch.delenv(env_name)
    importlib.reload(project_settings)


def test_hsts_seconds_is_env_backed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('SECURE_HSTS_SECONDS', '31536000')

    reloaded_settings = importlib.reload(project_settings)

    assert reloaded_settings.SECURE_HSTS_SECONDS == 31536000
    monkeypatch.delenv('SECURE_HSTS_SECONDS')
    importlib.reload(project_settings)
