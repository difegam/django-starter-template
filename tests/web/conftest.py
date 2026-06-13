from collections.abc import Generator

import pytest
from django.test import override_settings


@pytest.fixture(autouse=True)
def _use_staticfiles_storage() -> Generator[None]:
    """Use non-hashing static files storage during tests.

    CompressedManifestStaticFilesStorage requires a collectstatic manifest
    (staticfiles.json) that doesn't exist in the test environment. This
    fixture overrides the storage backend to the basic StaticFilesStorage
    so tests can render templates with {% static %} tags without errors.
    """
    with override_settings(
        STORAGES={
            'staticfiles': {
                'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
            },
        },
    ):
        yield
