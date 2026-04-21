import os
from collections.abc import Iterator
from typing import Any

import pytest


@pytest.fixture
def settings_overrides() -> Iterator[dict[str, str]]:
    """Minimal overrides for valid settings."""
    overrides = {
        "CLIENT_ID": "Foo",
        "CLIENT_SECRET": "bar",
        "DRY_RUN": "True",
        "SMTP_PORT": "1025",
        "SMTP_HOST": "mailcatcher",
        "SMTP_SECURITY": "none",
        "SENDER": "test@example.dk",
        "RECEIVERS": '["datagruppen@silkeborg.dk"]',
        "ACTIVE_AGENTS": "[]",
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
    """Set settings overrides as environmental variables."""
    for key, value in settings_overrides.items():
        if os.environ.get(key) is None:
            monkeypatch.setenv(key, value)
    yield settings_overrides
