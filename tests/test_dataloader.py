# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from mo_smtp.dataloaders import load_mo_org_unit_data
from mo_smtp.dataloaders import load_mo_user_data


@pytest.fixture
async def graphql_session_execute() -> AsyncGenerator:
    """
    Mocks a qraphql query execution
    """

    yield {
        "employees": {
            "employee1": "employee1",
            "employee2": "employee2",
        },
        "org_units": {
            "org_unit1": "org_unit1",
            "org_unit2": "org:unit2",
        },
    }


async def test_load_mo_user_data(graphql_session_execute: dict) -> None:

    uuid = uuid4()

    graphql_session = AsyncMock()
    graphql_session.execute.return_value = graphql_session_execute

    result = await load_mo_user_data([uuid], graphql_session)
    assert graphql_session_execute["employees"] == result


async def test_load_mo_org_unit_data(graphql_session_execute: dict) -> None:

    uuid = uuid4()

    graphql_session = AsyncMock()
    graphql_session.execute.return_value = graphql_session_execute

    result = await load_mo_org_unit_data([uuid], graphql_session)
    assert graphql_session_execute["org_units"] == result
