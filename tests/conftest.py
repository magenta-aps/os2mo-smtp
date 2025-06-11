import os
from collections.abc import Iterator
from typing import Any

import pytest

from mo_smtp.config import Settings


@pytest.fixture(scope="module")
def settings_overrides_module_scope() -> Iterator[dict[str, Any]]:
    """Fixture to construct dictionary of minimal overrides for valid settings."""
    overrides = {
        "CLIENT_ID": "Foo",
        "CLIENT_SECRET": "bar",
        "DRY_RUN": "True",
        "SMTP_PORT": "25",
        "SMTP_HOST": "smtp.host.com",
        "SMTP_SECURITY": "none",
        "FASTRAMQPI__AMQP__URL": "amqp://guest:guest@msg_broker:5672/",
        "FASTRAMQPI__DATABASE__USER": "fastramqpi",
        "FASTRAMQPI__DATABASE__PASSWORD": "fastramqpi",
        "FASTRAMQPI__DATABASE__HOST": "db",
        "FASTRAMQPI__DATABASE__NAME": "fastramqpi",
    }
    yield overrides


@pytest.fixture(scope="module")
def load_settings_overrides_module_scope(
    settings_overrides_module_scope: dict[str, Any],
) -> Iterator[dict[str, Any]]:
    """Fixture to set happy-path settings overrides as environmental variables."""
    monkeypatch = pytest.MonkeyPatch()
    for key, value in settings_overrides_module_scope.items():
        if os.environ.get(key) is None:
            monkeypatch.setenv(key, value)
        # Debugging line
        print(f"Set {key}={os.environ.get(key)}")
    yield settings_overrides_module_scope


@pytest.fixture
def settings_overrides() -> Iterator[dict[str, str]]:
    """Fixture to construct dictionary of minimal overrides for valid settings.

    Yields:
        Minimal set of overrides.
    """
    overrides = {
        "CLIENT_ID": "Foo",
        "CLIENT_SECRET": "bar",
        "DRY_RUN": "True",
        "SMTP_PORT": "25",
        "SMTP_HOST": "smtp.host.com",
        "SMTP_SECURITY": "none",
        "FASTRAMQPI__AMQP__URL": "amqp://guest:guest@msg_broker:5672/",
        "FASTRAMQPI__DATABASE__USER": "fastramqpi",
        "FASTRAMQPI__DATABASE__PASSWORD": "fastramqpi",
        "FASTRAMQPI__DATABASE__HOST": "db",
        "FASTRAMQPI__DATABASE__NAME": "fastramqpi",
    }
    yield overrides


@pytest.fixture
def load_settings_overrides(
    monkeypatch: pytest.MonkeyPatch,
    settings_overrides: dict[str, str],
) -> Iterator[dict[str, Any]]:
    """Fixture to set happy-path settings overrides as environmental variables."""
    for key, value in settings_overrides.items():
        if os.environ.get(key) is None:
            monkeypatch.setenv(key, value)
    yield settings_overrides


@pytest.fixture
def minimal_valid_settings(load_settings_overrides: None) -> Settings:
    return Settings()
