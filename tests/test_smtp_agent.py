# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# WOOHOO, deleted all my tests again, 'cause this sure doesn't make any sense to me
import asyncio
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastramqpi.context import Context
from ramqp.mo.models import PayloadType
from ramqp.utils import RejectMessage

from mo_smtp.config import Settings
from mo_smtp.smtp_agent import create_app
from mo_smtp.smtp_agent import listen_to_address_create


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """
    Fixture to set minimal required settings
    """

    monkeypatch.setenv("client_id", "foo")
    monkeypatch.setenv("client_secret", "bar")
    monkeypatch.setenv("testing", "True")

    return Settings()


@pytest.fixture
def gql_client() -> Iterator[AsyncMock]:
    yield AsyncMock()


@pytest.fixture
def context(
    gql_client: AsyncMock,
    settings: Settings,
) -> Context:
    context = Context(
        {
            "user_context": {
                "settings": settings,
                "gql_client": gql_client,
            },
        }
    )

    return context


def test_create_app(
    load_settings_overrides: dict[str, Any],
) -> None:
    """Test that we can construct our FastAPI application."""

    app = create_app()
    assert isinstance(app, FastAPI)


async def test_listen_to_address_create_no_engagements(
    context: dict[str, Any],
) -> None:
    """Test that listen_to_address_create method performs correctly"""

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

    async def load_mo_user(uuid: UUID, mo_users: Any) -> Any:
        """Mocks a graphql search for employees"""
        return employee

    async def load_mo_address(uuid: UUID, graphql_client: Any) -> dict[str, Any]:
        """Mocks a graphql search for email address"""
        return employee_address

    usermock = AsyncMock(side_effect=load_mo_user)
    addressmock = AsyncMock(side_effect=load_mo_address)
    payload = PayloadType(
        uuid=uuid_employee, object_uuid=uuid_address, time=datetime.now()
    )

    with patch("mo_smtp.smtp_agent.load_mo_user_data", usermock), patch(
        "mo_smtp.smtp_agent.send_email", MagicMock
    ), patch("mo_smtp.smtp_agent.load_mo_address_data", addressmock):
        await asyncio.gather(listen_to_address_create(context, payload))
        usermock.assert_any_await(uuid_employee, context["user_context"]["gql_client"])
        addressmock.assert_awaited_with(
            uuid_address, context["user_context"]["gql_client"]
        )


async def test_listen_to_address_create_multiple_engagements_with_manager(
    context: dict[str, Any],
) -> None:
    """Test that listen_to_address_create method performs correctly"""

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

    async def load_mo_user(uuid: UUID, mo_users: Any) -> Any:
        """Mocks a graphql search for employees"""
        if uuid == uuid_employee:
            return employee
        elif uuid == uuid_manager:
            return manager

    async def load_mo_address(uuid: UUID, graphql_client: Any) -> dict[str, Any]:
        """Mocks a graphql search for email address"""
        return employee_address

    usermock = AsyncMock(side_effect=load_mo_user)
    addressmock = AsyncMock(side_effect=load_mo_address)
    org_unit_mock = AsyncMock(side_effect=[ou1, ou2])
    payload = PayloadType(uuid=uuid_employee, object_uuid=uuid4(), time=datetime.now())

    with patch("mo_smtp.smtp_agent.load_mo_user_data", usermock), patch(
        "mo_smtp.smtp_agent.load_mo_org_unit_data", org_unit_mock
    ), patch("mo_smtp.smtp_agent.send_email", MagicMock), patch(
        "mo_smtp.smtp_agent.load_mo_address_data", addressmock
    ):
        await asyncio.gather(listen_to_address_create(context, payload))
        usermock.assert_any_await(uuid_employee, context["user_context"]["gql_client"])
        usermock.assert_awaited_with(
            uuid_manager, context["user_context"]["gql_client"]
        )
        org_unit_mock.assert_any_await(uuid_ou1, context["user_context"]["gql_client"])
        org_unit_mock.assert_any_await(uuid_ou2, context["user_context"]["gql_client"])


async def test_listen_to_address_create_not_email(
    context: dict[str, Any],
) -> None:
    """
    Tests that listen_to_address_create rejects amqp messages regarding addresses, that
    are not emails
    """

    uuid_address = uuid4()
    employee_address = {
        "name": "Arbitrary home address",
        "address_type": {"scope": "DAR"},
    }

    async def load_mo_address(uuid: UUID, graphql_client: Any) -> Any:
        """Mocks a graphql search for addresses"""
        return employee_address

    addressmock = AsyncMock(side_effect=load_mo_address)
    usermock = AsyncMock()
    payload = PayloadType(uuid=uuid4(), object_uuid=uuid_address, time=datetime.now())

    with patch("mo_smtp.smtp_agent.load_mo_user_data", usermock), patch(
        "mo_smtp.smtp_agent.load_mo_address_data", addressmock
    ):
        await asyncio.gather(listen_to_address_create(context, payload))
        addressmock.assert_awaited_once_with(
            uuid_address, context["user_context"]["gql_client"]
        )
        usermock.assert_not_awaited()


async def test_listen_to_address_create_object_uuid_is_message_uuid(
    context: dict[str, Any],
) -> None:
    """
    Tests that listen_to_address_create rejects messages where
    payload.uuid==payload.object_uuid, since that would refer to the creation of the
    employee
    """

    uuid_employee = uuid4()

    addressmock = AsyncMock()
    usermock = AsyncMock()
    payload = PayloadType(
        uuid=uuid_employee, object_uuid=uuid_employee, time=datetime.now()
    )

    with patch("mo_smtp.smtp_agent.load_mo_user_data", usermock), patch(
        "mo_smtp.smtp_agent.load_mo_address_data", addressmock
    ):
        await asyncio.gather(listen_to_address_create(context, payload))
        usermock.assert_not_awaited()
        addressmock.assert_not_awaited()


async def test_listen_to_address_create_invalid_user_email(
    context: dict[str, Any],
) -> None:
    """
    Tests that listen_to_address_create rejects messages with invalid emails
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

        async def load_mo_user(uuid: UUID, graphql_client: Any) -> Any:
            """Mocks a graphql search for employees"""
            return employee

        async def load_mo_address(uuid: UUID, graphql_client: Any) -> Any:
            """Mocks a graphql search for addresses"""
            return employee_address

        addressmock = AsyncMock(side_effect=load_mo_address)
        usermock = AsyncMock(side_effect=load_mo_user)
        payload = PayloadType(
            uuid=uuid_employee, object_uuid=uuid_address, time=datetime.now()
        )

        with patch("mo_smtp.smtp_agent.load_mo_user_data", usermock), patch(
            "mo_smtp.smtp_agent.load_mo_address_data", addressmock
        ), pytest.raises(RejectMessage):
            await asyncio.gather(listen_to_address_create(context, payload))


async def test_listen_to_address_create_multiple_email_addresses(
    context: dict[str, Any],
) -> None:
    """
    Tests that listen_to_address_create rejects messages where there already exists
    an email address
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

    async def load_mo_user(uuid: UUID, graphql_client: Any) -> Any:
        """Mocks a graphql search for employees"""
        return employee

    async def load_mo_address(uuid: UUID, graphql_client: Any) -> Any:
        """Mocks a graphql search for addresses"""
        return employee_address

    addressmock = AsyncMock(side_effect=load_mo_address)
    usermock = AsyncMock(side_effect=load_mo_user)
    payload = PayloadType(
        uuid=uuid_employee, object_uuid=uuid_address, time=datetime.now()
    )

    with patch("mo_smtp.smtp_agent.load_mo_user_data", usermock), patch(
        "mo_smtp.smtp_agent.load_mo_address_data", addressmock
    ):
        await asyncio.gather(listen_to_address_create(context, payload))
        usermock.assert_awaited_once_with(
            uuid_employee, context["user_context"]["gql_client"]
        )
        addressmock.assert_awaited_once_with(
            uuid_address, context["user_context"]["gql_client"]
        )
