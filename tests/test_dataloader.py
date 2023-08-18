# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
import datetime
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
import pytz  # type: ignore

from mo_smtp.dataloaders import DataLoader
from mo_smtp.dataloaders import mo_datestring_to_utc


@pytest.fixture
async def graphql_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def dataloader(graphql_session: AsyncMock) -> DataLoader:
    mo = AsyncMock()
    dataloader = DataLoader(mo)
    return dataloader


async def test_load_mo_user_data(dataloader: DataLoader) -> None:

    result = await dataloader.load_mo_user_data(uuid4())
    assert result is not None
    dataloader.mo.get_user_data.assert_awaited_once()


async def test_load_mo_org_unit_data(dataloader: DataLoader) -> None:

    result = await dataloader.load_mo_org_unit_data(uuid4())
    assert result is not None
    dataloader.mo.get_org_unit_data.assert_awaited_once()


async def test_load_mo_address_data(dataloader: DataLoader) -> None:
    result = await dataloader.load_mo_address_data(uuid4())
    assert result is not None
    dataloader.mo.get_address_data.assert_awaited_once()

    emtpy_mock = MagicMock()
    emtpy_mock.objects = []
    dataloader.mo.get_address_data.return_value = emtpy_mock
    result = await dataloader.load_mo_address_data(uuid4())
    assert result is None


async def test_load_mo_manager_data(dataloader: DataLoader):

    objects_mock = MagicMock()
    objects_mock.objects = [MagicMock()]
    manager_mock = MagicMock()
    manager_mock.objects = [objects_mock]
    dataloader.mo.get_manager_data.return_value = manager_mock

    result = await dataloader.load_mo_manager_data(uuid4())
    assert result is not None
    dataloader.mo.get_manager_data.assert_awaited_once()


async def test_load_mo_root_org_uuid(dataloader: DataLoader):
    root_org_uuid = uuid4()

    root_org_mock = AsyncMock()
    root_org_mock.uuid = root_org_uuid
    dataloader.mo.get_root_org.return_value = root_org_mock

    result = await dataloader.load_mo_root_org_uuid()
    assert result == root_org_uuid


async def test_get_org_unit_location(dataloader: DataLoader):
    root_org_uuid = str(uuid4())
    dataloader.load_mo_root_org_uuid = AsyncMock()  # type: ignore
    dataloader.load_mo_root_org_uuid.return_value = root_org_uuid

    root_org = {"uuid": root_org_uuid}

    org_unit_1 = {
        "parent_uuid": root_org_uuid,
        "name": "org1",
        "uuid": str(uuid4()),
    }
    org_unit_2 = {
        "parent_uuid": org_unit_1["uuid"],
        "name": "org2",
        "uuid": str(uuid4()),
    }

    org_unit_dict = {
        root_org["uuid"]: root_org,
        org_unit_1["uuid"]: org_unit_1,
        org_unit_2["uuid"]: org_unit_2,
    }

    async def load_org_unit_data(uuid):
        return org_unit_dict[uuid]

    dataloader.load_mo_org_unit_data = AsyncMock()  # type: ignore
    dataloader.load_mo_org_unit_data.side_effect = load_org_unit_data

    assert await dataloader.get_org_unit_location(org_unit_1) == "org1"
    assert await dataloader.get_org_unit_location(org_unit_2) == "org1 / org2"


def test_extract_latest_object(dataloader: DataLoader):

    uuid_obj1 = str(uuid4())
    uuid_obj2 = str(uuid4())
    uuid_obj3 = str(uuid4())

    datetime_mock = MagicMock(datetime)
    datetime_mock.datetime.utcnow.return_value = datetime.datetime(2022, 8, 10)
    datetime_mock.datetime.fromisoformat = datetime.datetime.fromisoformat
    with patch(
        "mo_smtp.dataloaders.datetime",
        datetime_mock,
    ):

        # One of the objects is valid today - return it
        obj1 = MagicMock()
        obj1.validity.from_ = datetime.datetime(2022, 8, 1)
        obj1.validity.to = datetime.datetime(2022, 8, 1)
        obj1.uuid = uuid_obj1

        obj2 = MagicMock()
        obj2.validity.from_ = datetime.datetime(2022, 8, 2)
        obj2.validity.to = datetime.datetime(2022, 8, 15)
        obj2.uuid = uuid_obj2

        obj3 = MagicMock()
        obj3.validity.from_ = datetime.datetime(2022, 8, 15)
        obj3.validity.to = None
        obj3.uuid = uuid_obj3

        objects = [obj1, obj2, obj3]

        assert dataloader.extract_current_or_latest_object(objects).uuid == uuid_obj2

        # One of the objects is valid today (without to-date) - return it
        obj1 = MagicMock()
        obj1.validity.from_ = datetime.datetime(2022, 8, 1)
        obj1.validity.to = datetime.datetime(2022, 8, 2)
        obj1.uuid = uuid_obj1

        obj2 = MagicMock()
        obj2.validity.from_ = datetime.datetime(2022, 8, 2)
        obj2.validity.to = None
        obj2.uuid = uuid_obj2

        objects = [obj1, obj2]
        assert dataloader.extract_current_or_latest_object(objects).uuid == uuid_obj2

        # One of the objects is valid today (without from-date)- return it
        obj1 = MagicMock()
        obj1.validity.from_ = None
        obj1.validity.to = datetime.datetime(2022, 8, 15)
        obj1.uuid = uuid_obj2

        obj2 = MagicMock()
        obj2.validity.from_ = datetime.datetime(2022, 8, 15)
        obj2.validity.to = None
        obj2.uuid = uuid_obj3

        objects = [obj1, obj2]
        assert dataloader.extract_current_or_latest_object(objects).uuid == uuid_obj2

        # No object is valid today - return the latest
        obj1 = MagicMock()
        obj1.validity.from_ = datetime.datetime(2022, 8, 1)
        obj1.validity.to = datetime.datetime(2022, 8, 2)
        obj1.uuid = uuid_obj1

        obj2 = MagicMock()
        obj2.validity.from_ = datetime.datetime(2022, 8, 15)
        obj2.validity.to = None
        obj2.uuid = uuid_obj3

        objects = [obj1, obj2]
        assert dataloader.extract_current_or_latest_object(objects).uuid == uuid_obj3

        # No object is valid today - return the latest
        obj1 = MagicMock()
        obj1.validity.from_ = datetime.datetime(2022, 8, 1)
        obj1.validity.to = datetime.datetime(2022, 8, 2)
        obj1.uuid = uuid_obj1

        obj2 = MagicMock()
        obj2.validity.from_ = datetime.datetime(2022, 8, 15)
        obj2.validity.to = datetime.datetime(2022, 8, 20)
        obj2.uuid = uuid_obj2

        objects = [obj1, obj2]
        assert dataloader.extract_current_or_latest_object(objects).uuid == uuid_obj2

        with pytest.raises(Exception):
            objects = []
            dataloader.extract_current_or_latest_object(objects)


def test_mo_datestring_to_utc():

    datetime_obj = datetime.datetime(
        2022, 8, 15, tzinfo=pytz.timezone("Europe/Copenhagen")
    )

    assert mo_datestring_to_utc(datetime_obj) == datetime.datetime(2022, 8, 15)
    assert mo_datestring_to_utc(None) is None
