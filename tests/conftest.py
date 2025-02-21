import os
from collections.abc import Iterator
from typing import Any

import pytest


@pytest.fixture(scope="module")
def settings_overrides() -> Iterator[dict[str, Any]]:
    """Fixture to construct dictionary of minimal overrides for valid settings.

    Yields:
        Minimal set of overrides.
    """
    overrides = {
        "client_id": "Foo",
        "client_secret": "bar",
        "testing": "True",
        "smtp_port": 25,
        "smtp_host": "smtp.host.com",
        "fastramqpi__amqp__url": "amqp://guest:guest@msg_broker:5672/",
    }
    yield overrides


@pytest.fixture(scope="module")
def load_settings_overrides(
    settings_overrides: dict[str, Any],
) -> Iterator[dict[str, Any]]:
    """Fixture to set happy-path settings overrides as environmental variables.

    Note:
        Only loads environmental variables, if variables are not already set.

    Args:
        settings_overrides: The list of settings to load in.
        monkeypatch: Pytest MonkeyPatch instance to set environmental variables.

    Yields:
        Minimal set of overrides.
    """
    monkeypatch = pytest.MonkeyPatch()
    for key, value in settings_overrides.items():
        if os.environ.get(key) is None:
            monkeypatch.setenv(key, value)
    yield settings_overrides
