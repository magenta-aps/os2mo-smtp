# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from unittest.mock import MagicMock

from fastapi import FastAPI

from mo_smtp.smtp_agent import amqp_router
from mo_smtp.smtp_agent import create_app
from mo_smtp.smtp_agent import register_agents


def test_create_app(
    load_settings_overrides: dict[str, Any],
) -> None:
    """Test that we can construct our FastAPI application."""

    app = create_app()
    assert isinstance(app, FastAPI)


def test_register_agents():

    agents_to_register = ["agent_1", "agent_2"]
    agents = MagicMock()

    assert len(amqp_router.registry) == 0
    register_agents(agents, agents_to_register)
    assert len(amqp_router.registry) == 2
