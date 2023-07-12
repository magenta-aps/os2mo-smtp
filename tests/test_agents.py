# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from ramqp.mo.models import MORoutingKey
from ramqp.mo.models import PayloadType
from structlog.testing import capture_logs

from mo_smtp.agents import Agents


@pytest.fixture
def dataloader() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def agents(dataloader: AsyncMock) -> Agents:
    context = Context({"user_context": {"dataloader": dataloader}})

    with patch("mo_smtp.agents.EmailClient", MagicMock()):
        agents = Agents(context)
    return agents


async def test_inform_manager_on_employee_address_creation_no_engagements(
    dataloader: AsyncMock, agents: Agents
) -> None:
    """
    Test that agents.inform_manager_on_employee_address_creation method performs
    correctly
    """

    uuid_employee = uuid4()
    uuid_address = uuid4()
    employee_address = {"name": "employee@test", "address_type": {"scope": "EMAIL"}}

    employee = {
        "name": "Test McTesterson",
        "uuid": str(uuid_employee),
        "addresses": [
            {
                "value": "employee@test",
                "address_type": {
                    "scope": "EMAIL",
                },
            },
        ],
        "engagements": [],
    }

    payload = PayloadType(
        uuid=uuid_employee, object_uuid=uuid_address, time=datetime.now()
    )
    dataloader.load_mo_address_data.return_value = employee_address
    dataloader.load_mo_user_data.return_value = employee
    agents.email_client = MagicMock()

    mo_routing_key = MORoutingKey.build("employee.address.create")
    await agents.inform_manager_on_employee_address_creation(
        payload, mo_routing_key=mo_routing_key
    )

    dataloader.load_mo_user_data.assert_any_await(uuid_employee)
    dataloader.load_mo_address_data.assert_awaited_with(uuid_address)


async def test_inform_manager_on_employee_address_creation_multiple_engagements(
    agents: Agents, dataloader: AsyncMock
) -> None:
    """
    Test that agents.inform_manager_on_employee_address_creation method performs
    correctly
    """

    uuid_employee = uuid4()
    uuid_ou1 = uuid4()
    uuid_ou2 = uuid4()
    uuid_manager = uuid4()
    employee_address = {"name": "employee@test", "address_type": {"scope": "EMAIL"}}

    employee = {
        "name": "Test McTesterson",
        "uuid": str(uuid_employee),
        "addresses": [
            {
                "value": "employee@test",
                "address_type": {
                    "scope": "EMAIL",
                },
            },
        ],
        "engagements": [
            {
                "name": "ou1",
                "org_unit_uuid": uuid_ou1,
            },
            {
                "name": "ou2",
                "org_unit_uuid": uuid_ou2,
            },
        ],
    }
    manager = {
        "name": "Manny O'ager",
        "uuid": str(uuid_manager),
        "addresses": [
            {
                "value": "manager@test",
                "address_type": {
                    "scope": "EMAIL",
                },
            },
        ],
    }
    ou1 = {
        "name": "ou1",
        "uuid": str(uuid_ou1),
        "managers": [
            {
                "employee_uuid": uuid_manager,
                "name": "Manny O'ager",
            },
        ],
    }
    ou2 = {
        "name": "ou2",
        "uuid": str(uuid_ou2),
        "managers": [],
    }

    async def load_mo_user(uuid: UUID) -> Any:
        """Mocks a graphql search for employees"""
        if uuid == uuid_employee:
            return employee
        elif uuid == uuid_manager:
            return manager

    payload = PayloadType(uuid=uuid_employee, object_uuid=uuid4(), time=datetime.now())
    mo_routing_key = MORoutingKey.build("employee.address.create")

    dataloader.load_mo_user_data = AsyncMock(side_effect=load_mo_user)
    dataloader.load_mo_address_data.return_value = employee_address
    dataloader.load_mo_org_unit_data = AsyncMock(side_effect=[ou1, ou2])
    agents.email_client = MagicMock()

    await agents.inform_manager_on_employee_address_creation(
        payload, mo_routing_key=mo_routing_key
    )

    dataloader.load_mo_user_data.assert_any_await(uuid_employee)
    dataloader.load_mo_user_data.assert_awaited_with(uuid_manager)
    dataloader.load_mo_org_unit_data.assert_any_await(uuid_ou1)
    dataloader.load_mo_org_unit_data.assert_any_await(uuid_ou2)


async def test_inform_manager_on_employee_address_creation_not_email(
    agents: Agents, dataloader: AsyncMock
) -> None:
    """
    Tests that agents.inform_manager_on_employee_address_creation rejects amqp
    messages regarding addresses, that are not emails
    """

    uuid_address = uuid4()
    employee_address = {
        "name": "Arbitrary home address",
        "address_type": {"scope": "DAR"},
    }

    async def load_mo_address(uuid: UUID) -> Any:
        """Mocks a graphql search for addresses"""
        return employee_address

    payload = PayloadType(uuid=uuid4(), object_uuid=uuid_address, time=datetime.now())
    mo_routing_key = MORoutingKey.build("employee.address.create")

    dataloader.load_mo_user_data = AsyncMock()
    dataloader.load_mo_address_data = AsyncMock(side_effect=load_mo_address)

    await agents.inform_manager_on_employee_address_creation(
        payload, mo_routing_key=mo_routing_key
    )

    dataloader.load_mo_address_data.assert_awaited_once_with(uuid_address)
    dataloader.load_mo_user_data.assert_not_awaited()


async def test_inform_manager_on_employee_address_creation_object_uuid_is_message_uuid(
    agents: Agents, dataloader: AsyncMock
) -> None:
    """
    Tests that agents.inform_manager_on_employee_address_creation rejects messages where
    payload.uuid==payload.object_uuid, since that would refer to the creation of the
    employee
    """

    uuid_employee = uuid4()

    payload = PayloadType(
        uuid=uuid_employee, object_uuid=uuid_employee, time=datetime.now()
    )
    mo_routing_key = MORoutingKey.build("employee.address.create")

    await agents.inform_manager_on_employee_address_creation(
        payload, mo_routing_key=mo_routing_key
    )

    dataloader.load_mo_user_data.assert_not_awaited()
    dataloader.load_mo_address_data.assert_not_awaited()


async def test_inform_manager_on_employee_address_creation_invalid_user_email(
    agents: Agents, dataloader: AsyncMock
) -> None:
    """
    Tests that agents.inform_manager_on_employee_address_creation rejects messages with
    invalid emails
    """

    for invalid_email in ["", "   ", "invalidemail"]:

        uuid_employee = uuid4()
        uuid_address = uuid4()
        employee_address = {"name": invalid_email, "address_type": {"scope": "EMAIL"}}
        employee = {
            "name": "Test McTesterson",
            "uuid": str(uuid_employee),
            "addresses": [
                {
                    "value": invalid_email,
                    "address_type": {
                        "scope": "EMAIL",
                    },
                },
            ],
        }

        payload = PayloadType(
            uuid=uuid_employee, object_uuid=uuid_address, time=datetime.now()
        )
        mo_routing_key = MORoutingKey.build("employee.address.create")

        dataloader.load_mo_user_data.return_value = employee
        dataloader.load_mo_address_data.return_value = employee_address

        await agents.inform_manager_on_employee_address_creation(
            payload, mo_routing_key=mo_routing_key
        )

        dataloader.load_mo_user_data.assert_awaited_once_with(uuid_employee)
        dataloader.load_mo_address_data.assert_awaited_once_with(uuid_address)
        dataloader.reset_mock()


async def test_inform_manager_on_employee_address_creation_multiple_email_addresses(
    agents: Agents, dataloader: AsyncMock
) -> None:
    """
    Tests that agents.inform_manager_on_employee_address_creation rejects messages
    where there already exists an email address
    """

    uuid_employee = uuid4()
    uuid_address = uuid4()
    employee_address = {"name": "new@email", "address_type": {"scope": "EMAIL"}}
    employee = {
        "name": "Test McTesterson",
        "uuid": str(uuid_employee),
        "addresses": [
            {"value": "old@email", "address_type": {"scope": "EMAIL"}},
            {"value": "new@email", "address_type": {"scope": "EMAIL"}},
        ],
    }

    payload = PayloadType(
        uuid=uuid_employee, object_uuid=uuid_address, time=datetime.now()
    )
    mo_routing_key = MORoutingKey.build("employee.address.create")

    dataloader.load_mo_user_data.return_value = employee
    dataloader.load_mo_address_data.return_value = employee_address

    await agents.inform_manager_on_employee_address_creation(
        payload, mo_routing_key=mo_routing_key
    )

    dataloader.load_mo_user_data.assert_awaited_once_with(uuid_employee)
    dataloader.load_mo_address_data.assert_awaited_once_with(uuid_address)


async def test_listen_to_address_wrong_routing_key(agents: Agents) -> None:
    """
    Tests that agents.inform_manager_on_employee_address_creation rejects amqp messages
    when routing key is not address.address.create
    """

    with capture_logs() as cap_logs:
        mo_routing_key = MORoutingKey.build("org_unit.org_unit.edit")
        payload = PayloadType(uuid=uuid4(), object_uuid=uuid4(), time=datetime.now())
        await agents.inform_manager_on_employee_address_creation(
            payload, mo_routing_key=mo_routing_key
        )

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        assert "Only listening to 'employee.address.create'" in str(messages)
