# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import MagicMock

from fastramqpi.ramqp.mo import MORouter

from mo_smtp.smtp_agent import register_agents


def test_register_agents():
    agents_to_register = ["agent_1"]

    amqp_router = MORouter()

    @amqp_router.register("address")
    def agent_1():
        pass

    @amqp_router.register("manager")
    def agent_2():
        pass

    amqpsystem = MagicMock()
    amqpsystem.router.registry = {}

    assert len(amqp_router.registry) == 2
    register_agents(amqp_router, amqpsystem, agents_to_register)
    assert len(amqp_router.registry) == 2
    assert len(amqpsystem.router.registry) == 1

    routing_keys = list(amqpsystem.router.registry.values())

    assert routing_keys[0] == {"address"}
