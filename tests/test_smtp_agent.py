# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# WOOHOO, deleted all my tests again, 'cause this sure doesn't make any sense to me
import asyncio
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
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
from mo_smtp.smtp_agent import listen_to_create


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """
    Fixture to set minimal required settings
    """

    monkeypatch.setenv("client_id", "foo")
    monkeypatch.setenv("client_secret", "bar")

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
    # fastramqpi: FastRAMQPI,
) -> None:
    """Test that we can construct our FastAPI application."""

    app = create_app()
    assert isinstance(app, FastAPI)


async def test_listen_to_create_multiple_engagements_with_manager(
    context: dict[str, Any],
) -> None:
    """Test that listen_to_create method performs correctly"""

    uuid_employee = uuid4()
    uuid_ou1 = uuid4()
    uuid_ou2 = uuid4()
    uuid_manager = uuid4()

    employee = {
        "objects": [
            {
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
        ],
    }
    manager = {
        "objects": [
            {
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
        ],
    }
    ou1 = {
        "objects": [
            {
                "name": "ou1",
                "uuid": str(uuid_ou1),
                "managers": [
                    {
                        "employee_uuid": uuid_manager,
                        "name": "Manny O'ager",
                    },
                ],
            }
        ],
    }
    ou2 = {
        "objects": [
            {
                "name": "ou2",
                "uuid": str(uuid_ou2),
                "managers": [],
            }
        ],
    }

    emailargs = {
        "sender": "noreply@saa-mo.gl",
        "smtp_port": 25,
        "smtp_host": "10.240.75.202",
        "testing": True,
        "texttype": "plain",
        "receiver": {employee["objects"][0]["addresses"][0]["value"]},  # type: ignore
        "cc": {manager["objects"][0]["addresses"][0]["value"]},  # type: ignore
        "subject": "Registrering i MO",
        "body": (
            "Denne besked er sendt som bekræftelse på at "
            f"{employee['objects'][0]['name']} er registreret i de "
            f"følgende enheder:\n{ou1['objects'][0]['name']},"
            f"\n{ou2['objects'][0]['name']}"
        ),
    }

    async def load_mo_user(uuid: list[UUID], mo_users: Any) -> list[Any] | None:
        """Mocks a graphql search for employees"""
        if uuid[0] == uuid_employee:
            return [employee]
        elif uuid[0] == uuid_manager:
            return [manager]
        else:
            return None

    async def load_mo_ou(uuid: list[UUID], mo_users: Any) -> list[Any]:
        """Mocks a graphql search for organisation units"""
        return [ou1, ou2]

    usermock = AsyncMock(side_effect=load_mo_user)
    org_unit_mock = AsyncMock(side_effect=load_mo_ou)
    emailmock = AsyncMock()
    payload = PayloadType(uuid=uuid_employee, object_uuid=uuid4(), time=datetime.now())

    with patch("mo_smtp.smtp_agent.load_mo_user_data", usermock), patch(
        "mo_smtp.smtp_agent.load_mo_org_unit_data", org_unit_mock
    ), patch("mo_smtp.smtp_agent.send_email", emailmock):
        await asyncio.gather(listen_to_create(context, payload))
        usermock.assert_any_await(
            [uuid_employee], context["user_context"]["gql_client"]
        )
        usermock.assert_awaited_with(
            [uuid_manager], context["user_context"]["gql_client"]
        )
        org_unit_mock.assert_awaited_once()
        org_unit_mock.assert_awaited_with(
            list(set([uuid_ou1, uuid_ou2])), context["user_context"]["gql_client"]
        )  # list(set(list)))-conversion to mimic the mechanics of the executed function
        emailmock.assert_awaited_with(**emailargs)


async def test_listen_to_create_no_user_email(
    context: dict[str, Any],
) -> None:
    """
    Tests that listen_to_create rejects messages where the employee does not have an
    email
    """

    uuid_employee = uuid4()
    employee = {
        "objects": [
            {
                "name": "Test McTesterson",
                "uuid": str(uuid_employee),
                "addresses": [
                    {},
                ],
            }
        ],
    }

    async def load_mo_user(uuid: list[UUID], mo_users: Any) -> list[Any] | None:
        """Mocks a graphql search for employees"""
        return [employee]

    usermock = AsyncMock(side_effect=load_mo_user)
    payload = PayloadType(uuid=uuid_employee, object_uuid=uuid4(), time=datetime.now())

    with patch("mo_smtp.smtp_agent.load_mo_user_data", usermock), pytest.raises(
        RejectMessage
    ):
        await asyncio.gather(listen_to_create(context, payload))
        usermock.assert_awaited_once_with(
            [uuid_employee], context["user_context"]["gql_client"]
        )