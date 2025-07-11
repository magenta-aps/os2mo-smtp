# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
import datetime
from datetime import timezone, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

from mo_smtp.autogenerated_graphql_client.address_data import (
    AddressDataAddresses,
    AddressDataAddressesObjectsCurrent,
)
from mo_smtp.autogenerated_graphql_client.employee_data import (
    EmployeeDataEmployees,
    EmployeeDataEmployeesObjectsCurrent,
)
from mo_smtp.autogenerated_graphql_client.employee_name import (
    EmployeeNameEmployees,
    EmployeeNameEmployeesObjectsCurrent,
)
from mo_smtp.autogenerated_graphql_client.manager_data import (
    ManagerDataManagersObjectsValidities,
)
from mo_smtp.autogenerated_graphql_client.institution_address import (
    InstitutionAddressOrgUnits,
)
from mo_smtp.autogenerated_graphql_client.manager_data import ManagerDataManagers
from mo_smtp.autogenerated_graphql_client.org_unit_ancestors import (
    OrgUnitAncestorsOrgUnits,
)
from mo_smtp.autogenerated_graphql_client.org_unit_data import (
    OrgUnitDataOrgUnits,
    OrgUnitDataOrgUnitsObjectsCurrent,
)
from mo_smtp.autogenerated_graphql_client.org_unit_relations import (
    OrgUnitRelationsOrgUnits,
    OrgUnitRelationsOrgUnitsObjects,
)
from mo_smtp.autogenerated_graphql_client.rolebinding import RolebindingRolebindings
from mo_smtp.autogenerated_graphql_client.ituser import (
    ItuserItusers,
    ItuserItusersObjectsCurrent,
)
from mo_smtp.dataloaders import (
    get_address_data,
    get_employee_data,
    get_employee_name,
    get_institution_address,
    get_manager_data,
    get_org_unit_data,
    get_org_unit_location,
)
from mo_smtp.dataloaders import get_org_unit_relations
from mo_smtp.dataloaders import get_ituser_uuid_by_rolebinding
from mo_smtp.dataloaders import get_ituser
from structlog.testing import capture_logs


async def test_get_address_data() -> None:
    address_uuid = uuid4()
    test_data = AddressDataAddressesObjectsCurrent.parse_obj(
        {
            "value": "test@example.com",
            "employee_uuid": uuid4(),
            "address_type": {"scope": "EMAIL"},
        }
    )

    mocked_mo_client = AsyncMock()
    mocked_mo_client.address_data.return_value = AddressDataAddresses.parse_obj(
        {"objects": [{"current": test_data}]}
    )
    address_data_response = await get_address_data(
        mo=mocked_mo_client, uuid=address_uuid
    )

    assert address_data_response == test_data
    mocked_mo_client.address_data.assert_awaited_once_with(address_uuid)


async def test_get_employee_data() -> None:
    employee_uuid = uuid4()
    test_data = EmployeeDataEmployeesObjectsCurrent.parse_obj(
        {
            "name": "Mick Jagger",
            "addresses": [{"value": "test@example.com"}],
            "engagements": [
                {
                    "org_unit": [{"name": "Stones"}],
                    "managers": [
                        {"person": [{"addresses": [{"value": "email@example.com"}]}]}
                    ],
                }
            ],
        }
    )

    mocked_mo_client = AsyncMock()
    mocked_mo_client.employee_data.return_value = EmployeeDataEmployees.parse_obj(
        {"objects": [{"current": test_data}]}
    )
    employee_data_response = await get_employee_data(
        mo=mocked_mo_client, uuid=employee_uuid
    )

    assert employee_data_response == test_data
    mocked_mo_client.employee_data.assert_awaited_once_with(employee_uuid)


async def test_get_employee_name() -> None:
    employee_uuid = uuid4()
    test_data = EmployeeNameEmployeesObjectsCurrent.parse_obj({"name": "Mick Jagger"})

    mocked_mo_client = AsyncMock()
    mocked_mo_client.employee_name.return_value = EmployeeNameEmployees.parse_obj(
        {"objects": [{"current": test_data}]}
    )
    employee_name_response = await get_employee_name(
        mo=mocked_mo_client, uuid=employee_uuid
    )

    assert employee_name_response == test_data
    mocked_mo_client.employee_name.assert_awaited_once_with(employee_uuid)


async def test_get_org_unit_data() -> None:
    org_unit_uuid = uuid4()
    test_data = OrgUnitDataOrgUnitsObjectsCurrent.parse_obj(
        {"name": "Rolling", "user_key": "123stones", "managers": []}
    )

    mocked_mo_client = AsyncMock()
    mocked_mo_client.org_unit_data.return_value = OrgUnitDataOrgUnits.parse_obj(
        {"objects": [{"current": test_data}]}
    )
    org_unit_data_response = await get_org_unit_data(
        mo=mocked_mo_client, uuid=org_unit_uuid
    )

    assert org_unit_data_response == test_data
    mocked_mo_client.org_unit_data.assert_awaited_once_with(org_unit_uuid)


async def test_get_manager_data():
    manager_uuid = uuid4()
    test_data = ManagerDataManagersObjectsValidities.parse_obj(
        {
            "employee_uuid": uuid4(),
            "org_unit_uuid": uuid4(),
            "validity": {
                "from": datetime.datetime(
                    2015,
                    1,
                    1,
                    tzinfo=timezone(timedelta(hours=1)),
                ),
                "to": None,
            },
        }
    )

    mocked_mo_client = AsyncMock()
    mocked_mo_client.manager_data.return_value = ManagerDataManagers.parse_obj(
        {"objects": [{"validities": [test_data]}]}
    )
    manager_data_response = await get_manager_data(
        mo=mocked_mo_client, uuid=manager_uuid
    )

    assert manager_data_response == test_data
    mocked_mo_client.manager_data.assert_awaited_once_with(manager_uuid)


async def test_get_org_unit_location():
    org_unit_uuid = uuid4()

    test_data = OrgUnitAncestorsOrgUnits.parse_obj(
        {
            "objects": [
                {
                    "current": {
                        "ancestors": [
                            {
                                "name": "And",
                            },
                            {
                                "name": "Stones",
                            },
                            {
                                "name": "Rolling",
                            },
                        ],
                        "name": "Friends",
                    }
                },
            ]
        }
    )

    mocked_mo_client = AsyncMock()
    mocked_mo_client.org_unit_ancestors.return_value = test_data
    org_unit_location_response = await get_org_unit_location(
        mo=mocked_mo_client, uuid=org_unit_uuid
    )
    assert org_unit_location_response == "Rolling / Stones / And / Friends"
    mocked_mo_client.org_unit_ancestors.assert_awaited_once_with(org_unit_uuid)


async def test_get_org_unit_relations():
    root_org = uuid4()
    org_unit_uuid = uuid4()
    test_data = [
        OrgUnitRelationsOrgUnitsObjects.parse_obj(
            {
                "current": {
                    "name": "org-unit-name",
                    "root": [{"uuid": root_org}],
                    "engagements": [
                        {"uuid": uuid4()},
                    ],
                    "related_units": [
                        {
                            "org_units": [
                                {
                                    "uuid": uuid4(),
                                    "root": [{"uuid": root_org}],
                                }
                            ]
                        }
                    ],
                }
            }
        )
    ]

    mocked_mo_client = AsyncMock()
    # mock org_unit_relations, which returns `data.org_units`
    mocked_mo_client.org_unit_relations.return_value = (
        OrgUnitRelationsOrgUnits.parse_obj({"objects": test_data})
    )

    # test that `get_org_unit_relations` returns the response from `org_unit_relations`.objects (which is what the test_data is)
    org_unit_relations_response = await get_org_unit_relations(
        mo=mocked_mo_client, org_unit_uuid=org_unit_uuid
    )

    assert org_unit_relations_response == test_data
    mocked_mo_client.org_unit_relations.assert_awaited_once_with(org_unit_uuid)


async def test_get_institution_address():
    root_org = uuid4()
    org_unit_uuid = uuid4()
    test_data = InstitutionAddressOrgUnits.parse_obj(
        {"objects": [{"current": {"addresses": [{"value": "test@test.dk"}]}}]}
    )

    mocked_mo_client = AsyncMock()

    mocked_mo_client.institution_address.return_value = test_data

    institution_address_response = await get_institution_address(
        mo=mocked_mo_client, root=root_org, uuid=org_unit_uuid
    )
    # expect a set of the email(s) in response
    expected_response = {"test@test.dk"}

    assert institution_address_response == expected_response
    mocked_mo_client.institution_address.assert_awaited_once_with(
        org_unit_uuid, root_org
    )


async def test_get_ituser_uuid_by_rolebinding() -> None:
    rolebinding_uuid = uuid4()
    ituser_uuid = uuid4()
    test_data = RolebindingRolebindings.parse_obj(
        {"objects": [{"current": {"ituser": [{"uuid": ituser_uuid}]}}]}
    )

    mocked_mo_client = AsyncMock()

    mocked_mo_client.rolebinding.return_value = test_data

    ituser_response = await get_ituser_uuid_by_rolebinding(
        mo=mocked_mo_client, uuid=rolebinding_uuid
    )
    expected_response = ituser_uuid

    assert ituser_response == expected_response
    mocked_mo_client.rolebinding.assert_awaited_once_with(rolebinding_uuid)


async def test_get_ituser_uuid_by_rolebinding_not_found() -> None:
    rolebinding_uuid = uuid4()
    test_data = RolebindingRolebindings.parse_obj({"objects": [{"current": None}]})

    mocked_mo_client = AsyncMock()

    mocked_mo_client.rolebinding.return_value = test_data

    ituser_response = await get_ituser_uuid_by_rolebinding(
        mo=mocked_mo_client, uuid=rolebinding_uuid
    )
    expected_response = None

    assert ituser_response == expected_response
    mocked_mo_client.rolebinding.assert_awaited_once_with(rolebinding_uuid)


async def test_get_ituser_uuid_by_rolebinding_empty_ituser() -> None:
    rolebinding_uuid = uuid4()
    test_data = RolebindingRolebindings.parse_obj(
        {"objects": [{"current": {"ituser": []}}]}
    )

    mocked_mo_client = AsyncMock()

    mocked_mo_client.rolebinding.return_value = test_data

    with capture_logs() as cap_logs:
        await get_ituser_uuid_by_rolebinding(mo=mocked_mo_client, uuid=rolebinding_uuid)

    mocked_mo_client.rolebinding.assert_awaited_once_with(rolebinding_uuid)

    assert (
        "Failed to fetch ituser from rolebinding UUID. This is usually caused by rolebinding events being fired, when it should've only been an ituser event"
        in str(cap_logs)
    )


async def test_get_ituser() -> None:
    ituser_uuid = uuid4()
    test_data = ItuserItusersObjectsCurrent.parse_obj(
        {
            "user_key": "ADUSER-123",
            "rolebindings": [
                {"role": [{"name": "admin", "uuid": uuid4()}]},
                {"role": [{"name": "user", "uuid": uuid4()}]},
            ],
            "person": [{"name": "Mick Jagger", "uuid": uuid4()}],
            "itsystem": {"name": "Active Directory", "uuid": uuid4()},
        }
    )

    mocked_mo_client = AsyncMock()

    mocked_mo_client.ituser.return_value = ItuserItusers.parse_obj(
        {"objects": [{"current": test_data}]}
    )

    ituser_response = await get_ituser(mo=mocked_mo_client, uuid=ituser_uuid)

    expected_response = test_data

    assert ituser_response == expected_response
    mocked_mo_client.ituser.assert_awaited_once_with(ituser_uuid)
