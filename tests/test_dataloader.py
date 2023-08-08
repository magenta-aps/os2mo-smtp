# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastramqpi.context import Context

from mo_smtp.dataloaders import DataLoader


@pytest.fixture
async def graphql_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def dataloader(graphql_session: AsyncMock) -> DataLoader:
    context = Context({"user_context": {"gql_client": graphql_session}})
    return DataLoader(context)


@pytest.fixture
async def graphql_session_execute() -> AsyncGenerator:
    """
    Mocks a qraphql query execution
    """

    yield {
        "employees": [{"objects": [{"name": "Jack"}]}],
        "org_units": [{"objects": [{"name": "Jack's organisation"}]}],
        "addresses": [
            {"current": {"name": "jack@place.net", "address_type": {"scope": "EMAIL"}}}
        ],
    }


async def test_load_mo_user_data(
    dataloader: DataLoader, graphql_session_execute: dict
) -> None:

    uuid = uuid4()

    dataloader.gql_client.execute.return_value = graphql_session_execute

    result = await dataloader.load_mo_user_data(uuid)
    assert graphql_session_execute["employees"][0]["objects"][0] == result


async def test_load_mo_org_unit_data(
    dataloader: DataLoader, graphql_session_execute: dict
) -> None:

    uuid = uuid4()

    dataloader.gql_client.execute.return_value = graphql_session_execute

    result = await dataloader.load_mo_org_unit_data(uuid)
    assert graphql_session_execute["org_units"][0]["objects"][0] == result


async def test_load_mo_address_data(
    dataloader: DataLoader, graphql_session_execute: dict
) -> None:

    uuid = uuid4()

    dataloader.gql_client.execute.return_value = graphql_session_execute

    result = await dataloader.load_mo_address_data(uuid)
    assert graphql_session_execute["addresses"][0]["current"] == result

    dataloader.gql_client.execute.return_value = {"addresses": []}

    result = await dataloader.load_mo_address_data(uuid)
    assert result is None
