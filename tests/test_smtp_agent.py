# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mo_smtp.smtp_agent import amqp_router
from mo_smtp.smtp_agent import create_app
from mo_smtp.smtp_agent import register_agents


@pytest.fixture(scope="module")
def app(
    load_settings_overrides: dict[str, Any],
) -> Iterator[FastAPI]:
    """Test that we can construct our FastAPI application."""

    with patch("mo_smtp.smtp_agent.Agents", MagicMock()), patch(
        "mo_smtp.smtp_agent.EmailClient", MagicMock()
    ):
        yield create_app()


@pytest.fixture(scope="module")
def test_client(app: FastAPI) -> Iterator[TestClient]:
    """Fixture to construct a FastAPI test-client.

    Note:
        The app does not do lifecycle management.

    Yields:
        TestClient for the FastAPI application.
    """
    yield TestClient(app)


def test_create_app(
    app: Iterator[FastAPI],
) -> None:
    """Test that we can construct our FastAPI application."""

    assert isinstance(app, FastAPI)


def test_register_agents():

    agents_to_register = ["agent_1:address", "agent_2:manager"]
    agents = MagicMock()
    agents.agent_1.__name__ = "agent_1"
    agents.agent_2.__name__ = "agent_2"

    assert len(amqp_router.registry) == 0
    register_agents(agents, agents_to_register)
    assert len(amqp_router.registry) == 2

    routing_keys = list(amqp_router.registry.values())

    assert routing_keys[0] == {"address"}
    assert routing_keys[1] == {"manager"}


def test_send_test_mail(test_client: TestClient):
    params = {"receiver": "nj@magenta-aps.dk"}
    response = test_client.post("/send_test_email", params=params)
    assert response.status_code == 202
