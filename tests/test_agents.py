# -*- coding: utf-8 -*-
import datetime
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
import pytz  # type: ignore
from fastramqpi.context import Context
from structlog.testing import capture_logs

from mo_smtp.agents import alert_on_manager_removal
from mo_smtp.agents import inform_manager_on_employee_address_creation


@pytest.fixture
def dataloader() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def DataLoader(dataloader: AsyncMock) -> MagicMock:
    DataLoader = MagicMock()
    DataLoader.return_value = dataloader
    return DataLoader


@pytest.fixture
def email_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def context(dataloader: AsyncMock, email_client: MagicMock) -> Context:
    email_settings = MagicMock()
    email_settings.receivers = ["datagruppen@silkeborg.dk"]

    return Context(
        {
            "user_context": {
                "dataloader": dataloader,
                "email_client": email_client,
                "email_settings": email_settings,
            }
        }
    )


async def test_inform_manager_on_employee_address_creation_no_engagements(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
) -> None:
    """
    Test that inform_manager_on_employee_address_creation method performs
    correctly
    """

    uuid_employee = str(uuid4())
    uuid_address = uuid4()
    employee_address = {
        "name": "employee@test",
        "employee_uuid": uuid_employee,
        "address_type": {"scope": "EMAIL"},
    }

    employee = {
        "name": "Test McTesterson",
        "uuid": str(uuid_employee),
        "addresses": [
            {
                "value": "employee@test",
                "employee_uuid": uuid_employee,
                "address_type": {
                    "scope": "EMAIL",
                },
            },
        ],
        "engagements": [],
    }

    dataloader.load_mo_address_data.return_value = employee_address
    dataloader.load_mo_user_data.return_value = employee

    with patch("mo_smtp.agents.DataLoader", DataLoader):
        await inform_manager_on_employee_address_creation(
            context, uuid_address, None, None
        )

    dataloader.load_mo_user_data.assert_any_await(uuid_employee)
    dataloader.load_mo_address_data.assert_awaited_with(uuid_address)


async def test_inform_manager_on_employee_address_creation_multiple_engagements(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
) -> None:
    """
    Test that inform_manager_on_employee_address_creation method performs
    correctly
    """

    uuid_employee = str(uuid4())
    uuid_ou1 = str(uuid4())
    uuid_ou2 = str(uuid4())
    uuid_manager = str(uuid4())
    employee_address = {
        "name": "employee@test",
        "employee_uuid": uuid_employee,
        "address_type": {"scope": "EMAIL"},
    }

    employee = {
        "name": "Test McTesterson",
        "uuid": uuid_employee,
        "addresses": [
            {
                "value": "employee@test",
                "employee_uuid": uuid_employee,
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
        "uuid": uuid_manager,
        "addresses": [
            {
                "value": "manager@test",
                "employee_uuid": uuid_manager,
                "address_type": {
                    "scope": "EMAIL",
                },
            },
        ],
    }
    ou1 = {
        "name": "ou1",
        "uuid": uuid_ou1,
        "managers": [
            {
                "employee_uuid": uuid_manager,
                "name": "Manny O'ager",
            },
            {
                "employee_uuid": None,  # employee_uuid is optional in MO
                "name": "Manny O'ager",
            },
        ],
    }
    ou2 = {
        "name": "ou2",
        "uuid": uuid_ou2,
        "managers": [],
    }

    async def load_mo_user(uuid: UUID) -> Any:
        """Mocks a graphql search for employees"""
        if uuid == uuid_employee:
            return employee
        elif uuid == uuid_manager:
            return manager

    dataloader.load_mo_user_data = AsyncMock(side_effect=load_mo_user)
    dataloader.load_mo_address_data.return_value = employee_address
    dataloader.load_mo_org_unit_data = AsyncMock(side_effect=[ou1, ou2])

    with patch("mo_smtp.agents.DataLoader", DataLoader):
        await inform_manager_on_employee_address_creation(context, uuid4(), None, None)

    dataloader.load_mo_user_data.assert_any_await(uuid_employee)
    dataloader.load_mo_user_data.assert_awaited_with(uuid_manager)
    dataloader.load_mo_org_unit_data.assert_any_await(uuid_ou1)
    dataloader.load_mo_org_unit_data.assert_any_await(uuid_ou2)


async def test_inform_manager_on_employee_address_creation_not_email(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
) -> None:
    """
    Tests that inform_manager_on_employee_address_creation rejects amqp
    messages regarding addresses, that are not emails
    """

    uuid_address = uuid4()
    uuid_employee = str(uuid4())
    employee_address = {
        "name": "Arbitrary home address",
        "employee_uuid": uuid_employee,
        "address_type": {"scope": "DAR"},
    }

    dataloader.load_mo_address_data.return_value = employee_address

    with patch("mo_smtp.agents.DataLoader", DataLoader):
        await inform_manager_on_employee_address_creation(
            context, uuid_address, None, None
        )

    dataloader.load_mo_address_data.assert_awaited_once_with(uuid_address)
    dataloader.load_mo_user_data.assert_not_awaited()


async def test_inform_manager_on_employee_address_creation_invalid_user_email(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
) -> None:
    """
    Tests that inform_manager_on_employee_address_creation rejects messages with
    invalid emails
    """

    for invalid_email in ["", "   ", "invalidemail"]:

        uuid_employee = str(uuid4())
        uuid_address = uuid4()
        employee_address = {
            "name": invalid_email,
            "employee_uuid": uuid_employee,
            "address_type": {"scope": "EMAIL"},
        }
        employee = {
            "name": "Test McTesterson",
            "uuid": str(uuid_employee),
            "addresses": [
                {
                    "value": invalid_email,
                    "employee_uuid": uuid_employee,
                    "address_type": {
                        "scope": "EMAIL",
                    },
                },
            ],
        }

        dataloader.load_mo_user_data.return_value = employee
        dataloader.load_mo_address_data.return_value = employee_address

        with patch("mo_smtp.agents.DataLoader", DataLoader):
            await inform_manager_on_employee_address_creation(
                context, uuid_address, None, None
            )

        dataloader.load_mo_user_data.assert_awaited_once_with(uuid_employee)
        dataloader.load_mo_address_data.assert_awaited_once_with(uuid_address)
        dataloader.reset_mock()


async def test_inform_manager_on_employee_address_creation_multiple_email_addresses(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
) -> None:
    """
    Tests that inform_manager_on_employee_address_creation rejects messages
    where there already exists an email address
    """

    uuid_employee = str(uuid4())
    uuid_address = uuid4()
    employee_address = {
        "name": "new@email",
        "employee_uuid": uuid_employee,
        "address_type": {"scope": "EMAIL"},
    }
    employee = {
        "name": "Test McTesterson",
        "uuid": uuid_employee,
        "addresses": [
            {
                "value": "old@email",
                "employee_uuid": uuid_employee,
                "address_type": {"scope": "EMAIL"},
            },
            {
                "value": "new@email",
                "employee_uuid": uuid_employee,
                "address_type": {"scope": "EMAIL"},
            },
        ],
    }

    dataloader.load_mo_user_data.return_value = employee
    dataloader.load_mo_address_data.return_value = employee_address

    with patch("mo_smtp.agents.DataLoader", DataLoader):
        await inform_manager_on_employee_address_creation(
            context, uuid_address, None, None
        )

    dataloader.load_mo_user_data.assert_awaited_once_with(uuid_employee)
    dataloader.load_mo_address_data.assert_awaited_once_with(uuid_address)


async def test_inform_manager_on_org_unit_address_creation(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
):

    org_unit_address = {
        "name": "new@email",
        "employee_uuid": None,
        "address_type": {"scope": "EMAIL"},
    }

    dataloader.load_mo_address_data.return_value = org_unit_address

    with capture_logs() as cap_logs:
        with patch("mo_smtp.agents.DataLoader", DataLoader):
            await inform_manager_on_employee_address_creation(
                context, uuid4(), None, None
            )
        assert "The address does not belong to an employee" in str(cap_logs)


async def test_alert_on_manager_removal_currently_employed(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
):
    manager = {
        "employee_uuid": uuid4(),
        "org_unit_uuid": uuid4(),
        "validity": {"to": None},
    }

    dataloader.load_mo_manager_data.return_value = manager
    with capture_logs() as cap_logs:
        with patch("mo_smtp.agents.DataLoader", DataLoader):
            await alert_on_manager_removal(context, uuid4(), None, None)
        assert "Manager is currently employed" in str(cap_logs)


async def test_alert_on_manager_removal_future_to_date(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
):
    manager = {
        "employee_uuid": uuid4(),
        "org_unit_uuid": uuid4(),
        "validity": {
            "to": datetime.datetime(
                2090, 1, 1, tzinfo=pytz.timezone("Europe/Copenhagen")
            )
        },
    }

    dataloader.load_mo_manager_data.return_value = manager
    with capture_logs() as cap_logs:
        with patch("mo_smtp.agents.DataLoader", DataLoader):
            await alert_on_manager_removal(context, uuid4(), None, None)
        assert "to_date is in the future" in str(cap_logs)


async def test_alert_on_manager_removal_past_to_date(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
):
    manager = {
        "employee_uuid": uuid4(),
        "org_unit_uuid": uuid4(),
        "validity": {
            "to": datetime.datetime(
                2000, 1, 1, tzinfo=pytz.timezone("Europe/Copenhagen")
            )
        },
    }

    dataloader.load_mo_manager_data.return_value = manager

    dataloader.load_mo_user_data.return_value = {"name": "Mick Jagger"}
    dataloader.load_mo_org_unit_data.return_value = {"user_key": "123stones"}
    dataloader.get_org_unit_location = AsyncMock()  # type: ignore
    dataloader.get_org_unit_location.return_value = "Rolling / Stones"
    with patch("mo_smtp.agents.DataLoader", DataLoader):
        await alert_on_manager_removal(context, uuid4(), None, None)
    email_client = context["user_context"]["email_client"]
    email_client.send_email.assert_called_once()

    call_args = email_client.send_email.call_args_list[0]

    receiver, header, message, _ = call_args.args
    assert receiver == ["datagruppen@silkeborg.dk"]
    assert header == "En medarbejder er blevet fjernet fra lederfanen"
    assert "123stones" in message
    assert "Mick Jagger" in message
    assert "Rolling / Stones" in message


async def test_alert_on_manager_removal_unknown_employee(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
):
    manager = {
        "employee_uuid": None,
        "org_unit_uuid": uuid4(),
        "validity": {
            "to": datetime.datetime(
                2000, 1, 1, tzinfo=pytz.timezone("Europe/Copenhagen")
            )
        },
    }

    dataloader.load_mo_manager_data.return_value = manager
    dataloader.get_org_unit_location = AsyncMock()  # type: ignore
    with patch("mo_smtp.agents.DataLoader", DataLoader):
        await alert_on_manager_removal(context, uuid4(), None, None)
    email_client = context["user_context"]["email_client"]

    email_client.send_email.assert_called_once()
    call_args = email_client.send_email.call_args_list[0]
    receiver, header, message, _ = call_args.args
    assert "Unknown employee" in message


async def test_inform_manager_address_not_found(
    DataLoader: MagicMock, dataloader: AsyncMock, context: Context
):

    dataloader.load_mo_address_data.return_value = None

    with capture_logs() as cap_logs:
        with patch("mo_smtp.agents.DataLoader", DataLoader):
            await inform_manager_on_employee_address_creation(
                context, uuid4(), None, None
            )
        assert "Address not found" in str(cap_logs)
