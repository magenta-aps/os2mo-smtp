from datetime import datetime
from uuid import UUID

from ._testing__create_address import (
    TestingCreateAddress,
    TestingCreateAddressAddressCreate,
)
from ._testing__create_class import TestingCreateClass, TestingCreateClassClassCreate
from ._testing__create_employee import (
    TestingCreateEmployee,
    TestingCreateEmployeeEmployeeCreate,
)
from ._testing__create_engagement import (
    TestingCreateEngagement,
    TestingCreateEngagementEngagementCreate,
)
from ._testing__create_it_system import (
    TestingCreateItSystem,
    TestingCreateItSystemItsystemCreate,
)
from ._testing__create_it_user import (
    TestingCreateItUser,
    TestingCreateItUserItuserCreate,
)
from ._testing__create_manager import (
    TestingCreateManager,
    TestingCreateManagerManagerCreate,
)
from ._testing__create_org_unit import (
    TestingCreateOrgUnit,
    TestingCreateOrgUnitOrgUnitCreate,
)
from ._testing__create_org_unit_address import (
    TestingCreateOrgUnitAddress,
    TestingCreateOrgUnitAddressAddressCreate,
)
from ._testing__create_org_unit_root import (
    TestingCreateOrgUnitRoot,
    TestingCreateOrgUnitRootOrgUnitCreate,
)
from ._testing__create_related_units import (
    TestingCreateRelatedUnits,
    TestingCreateRelatedUnitsRelatedUnitsUpdate,
)
from ._testing__create_rolebinding import (
    TestingCreateRolebinding,
    TestingCreateRolebindingRolebindingCreate,
)
from ._testing__get_email_address_type import (
    TestingGetEmailAddressType,
    TestingGetEmailAddressTypeFacets,
)
from ._testing__get_engagement_type import (
    TestingGetEngagementType,
    TestingGetEngagementTypeFacets,
)
from ._testing__get_job_function import (
    TestingGetJobFunction,
    TestingGetJobFunctionFacets,
)
from ._testing__get_manager_level import (
    TestingGetManagerLevel,
    TestingGetManagerLevelClasses,
)
from ._testing__get_manager_responsibility import (
    TestingGetManagerResponsibility,
    TestingGetManagerResponsibilityClasses,
)
from ._testing__get_manager_type import (
    TestingGetManagerType,
    TestingGetManagerTypeClasses,
)
from ._testing__get_org_unit_address_type import (
    TestingGetOrgUnitAddressType,
    TestingGetOrgUnitAddressTypeFacets,
)
from ._testing__get_org_unit_type import (
    TestingGetOrgUnitType,
    TestingGetOrgUnitTypeClasses,
)
from ._testing__get_related_units_for_org_unit import (
    TestingGetRelatedUnitsForOrgUnit,
    TestingGetRelatedUnitsForOrgUnitRelatedUnits,
)
from ._testing__get_role_facet import TestingGetRoleFacet, TestingGetRoleFacetFacets
from ._testing__get_role_type import TestingGetRoleType, TestingGetRoleTypeFacets
from ._testing__terminate_manager import (
    TestingTerminateManager,
    TestingTerminateManagerManagerTerminate,
)
from ._testing__terminate_org_unit import (
    TestingTerminateOrgUnit,
    TestingTerminateOrgUnitOrgUnitTerminate,
)
from ._testing__update_manager import (
    TestingUpdateManager,
    TestingUpdateManagerManagerUpdate,
)
from .address_data import AddressData, AddressDataAddresses
from .async_base_client import AsyncBaseClient
from .base_model import UNSET, UnsetType
from .employee_data import EmployeeData, EmployeeDataEmployees
from .employee_name import EmployeeName, EmployeeNameEmployees
from .institution_address import InstitutionAddress, InstitutionAddressOrgUnits
from .ituser import Ituser, ItuserItusers
from .manager_data import ManagerData, ManagerDataManagers
from .org_unit_address import OrgUnitAddress, OrgUnitAddressOrgUnits
from .org_unit_ancestors import OrgUnitAncestors, OrgUnitAncestorsOrgUnits
from .org_unit_data import OrgUnitData, OrgUnitDataOrgUnits
from .org_unit_relations import OrgUnitRelations, OrgUnitRelationsOrgUnits
from .related_unit_registrations import (
    RelatedUnitRegistrations,
    RelatedUnitRegistrationsRelatedUnits,
)
from .rolebinding import Rolebinding, RolebindingRolebindings


def gql(q: str) -> str:
    return q


class GraphQLClient(AsyncBaseClient):
    async def manager_data(self, uuid: UUID) -> ManagerDataManagers:
        query = gql(
            """
            query managerData($uuid: UUID!) {
              managers(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    employee_uuid
                    org_unit_uuid
                    validity {
                      to
                      from
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ManagerData.parse_obj(data).managers

    async def employee_data(self, uuid: UUID) -> EmployeeDataEmployees:
        query = gql(
            """
            query employeeData($uuid: UUID!) {
              employees(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    name
                    addresses(filter: {address_type: {scope: "EMAIL"}}) {
                      value
                    }
                    engagements {
                      org_unit {
                        name
                      }
                      managers(exclude_self: true) {
                        person {
                          addresses(filter: {address_type: {scope: "EMAIL"}}) {
                            value
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return EmployeeData.parse_obj(data).employees

    async def employee_name(self, uuid: UUID) -> EmployeeNameEmployees:
        query = gql(
            """
            query employeeName($uuid: UUID!) {
              employees(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    name
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return EmployeeName.parse_obj(data).employees

    async def org_unit_ancestors(self, uuid: UUID) -> OrgUnitAncestorsOrgUnits:
        query = gql(
            """
            query orgUnitAncestors($uuid: UUID!) {
              org_units(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    ancestors {
                      name
                    }
                    name
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitAncestors.parse_obj(data).org_units

    async def org_unit_data(self, uuid: UUID) -> OrgUnitDataOrgUnits:
        query = gql(
            """
            query orgUnitData($uuid: UUID!) {
              org_units(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    name
                    user_key
                    root {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitData.parse_obj(data).org_units

    async def address_data(self, uuid: UUID) -> AddressDataAddresses:
        query = gql(
            """
            query addressData($uuid: UUID!) {
              addresses(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    value
                    employee_uuid
                    address_type {
                      scope
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AddressData.parse_obj(data).addresses

    async def org_unit_relations(self, uuid: UUID) -> OrgUnitRelationsOrgUnits:
        query = gql(
            """
            query orgUnitRelations($uuid: UUID!) {
              org_units(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    name
                    root {
                      uuid
                    }
                    engagements {
                      uuid
                    }
                    related_units {
                      org_units {
                        uuid
                        root {
                          uuid
                        }
                      }
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitRelations.parse_obj(data).org_units

    async def institution_address(
        self, uuid: UUID, root: UUID
    ) -> InstitutionAddressOrgUnits:
        query = gql(
            """
            query institutionAddress($uuid: UUID!, $root: UUID!) {
              org_units(filter: {parent: {uuids: [$root]}, descendant: {uuids: [$uuid]}}) {
                objects {
                  current {
                    addresses(filter: {address_type: {scope: "EMAIL"}}) {
                      value
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid, "root": root}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InstitutionAddress.parse_obj(data).org_units

    async def org_unit_address(self, uuid: UUID) -> OrgUnitAddressOrgUnits:
        query = gql(
            """
            query orgUnitAddress($uuid: UUID!) {
              org_units(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    addresses(filter: {address_type: {scope: "EMAIL"}}) {
                      value
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitAddress.parse_obj(data).org_units

    async def related_unit_registrations(
        self, uuid: UUID
    ) -> RelatedUnitRegistrationsRelatedUnits:
        query = gql(
            """
            query relatedUnitRegistrations($uuid: UUID!) {
              related_units(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  registrations {
                    validities {
                      org_units_response {
                        objects {
                          uuid
                          current {
                            root {
                              uuid
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return RelatedUnitRegistrations.parse_obj(data).related_units

    async def rolebinding(self, uuid: UUID) -> RolebindingRolebindings:
        query = gql(
            """
            query rolebinding($uuid: UUID!) {
              rolebindings(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    ituser {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return Rolebinding.parse_obj(data).rolebindings

    async def ituser(self, uuid: UUID) -> ItuserItusers:
        query = gql(
            """
            query ituser($uuid: UUID!) {
              itusers(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    user_key
                    rolebindings {
                      role {
                        name
                        uuid
                      }
                    }
                    person {
                      name
                      uuid
                    }
                    itsystem {
                      name
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return Ituser.parse_obj(data).itusers

    async def _testing__get_org_unit_type(self) -> TestingGetOrgUnitTypeClasses:
        query = gql(
            """
            query _Testing_GetOrgUnitType {
              classes(filter: {facet_user_keys: "org_unit_type"}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetOrgUnitType.parse_obj(data).classes

    async def _testing__get_email_address_type(
        self,
    ) -> TestingGetEmailAddressTypeFacets:
        query = gql(
            """
            query _Testing_GetEmailAddressType {
              facets(filter: {user_keys: "employee_address_type"}) {
                objects {
                  current {
                    classes(filter: {scope: "EMAIL"}) {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetEmailAddressType.parse_obj(data).facets

    async def _testing__get_org_unit_address_type(
        self,
    ) -> TestingGetOrgUnitAddressTypeFacets:
        query = gql(
            """
            query _Testing_GetOrgUnitAddressType {
              facets(filter: {user_keys: "org_unit_address_type"}) {
                objects {
                  current {
                    classes(filter: {scope: "EMAIL"}) {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetOrgUnitAddressType.parse_obj(data).facets

    async def _testing__get_manager_level(self) -> TestingGetManagerLevelClasses:
        query = gql(
            """
            query _Testing_GetManagerLevel {
              classes(filter: {facet_user_keys: "manager_level"}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetManagerLevel.parse_obj(data).classes

    async def _testing__get_manager_type(self) -> TestingGetManagerTypeClasses:
        query = gql(
            """
            query _Testing_GetManagerType {
              classes(filter: {facet_user_keys: "manager_type"}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetManagerType.parse_obj(data).classes

    async def _testing__get_manager_responsibility(
        self,
    ) -> TestingGetManagerResponsibilityClasses:
        query = gql(
            """
            query _Testing_GetManagerResponsibility {
              classes(filter: {facet_user_keys: "responsibility"}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetManagerResponsibility.parse_obj(data).classes

    async def _testing__get_engagement_type(self) -> TestingGetEngagementTypeFacets:
        query = gql(
            """
            query _Testing_GetEngagementType {
              facets(filter: {user_keys: "engagement_type"}) {
                objects {
                  current {
                    classes {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetEngagementType.parse_obj(data).facets

    async def _testing__get_job_function(self) -> TestingGetJobFunctionFacets:
        query = gql(
            """
            query _Testing_GetJobFunction {
              facets(filter: {user_keys: "engagement_job_function"}) {
                objects {
                  current {
                    classes {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetJobFunction.parse_obj(data).facets

    async def _testing__create_org_unit_root(
        self, name: str, root_uuid: UUID, org_unit_type: UUID, from_: datetime
    ) -> TestingCreateOrgUnitRootOrgUnitCreate:
        query = gql(
            """
            mutation _Testing_CreateOrgUnitRoot($name: String!, $root_uuid: UUID!, $org_unit_type: UUID!, $from: DateTime!) {
              org_unit_create(
                input: {uuid: $root_uuid, name: $name, org_unit_type: $org_unit_type, validity: {from: $from}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "name": name,
            "root_uuid": root_uuid,
            "org_unit_type": org_unit_type,
            "from": from_,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateOrgUnitRoot.parse_obj(data).org_unit_create

    async def _testing__create_org_unit(
        self,
        name: str,
        parent: UUID,
        org_unit_type: UUID,
        from_: datetime,
        to: datetime | None | UnsetType = UNSET,
    ) -> TestingCreateOrgUnitOrgUnitCreate:
        query = gql(
            """
            mutation _Testing_CreateOrgUnit($name: String!, $parent: UUID!, $org_unit_type: UUID!, $from: DateTime!, $to: DateTime) {
              org_unit_create(
                input: {name: $name, parent: $parent, org_unit_type: $org_unit_type, validity: {from: $from, to: $to}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "name": name,
            "parent": parent,
            "org_unit_type": org_unit_type,
            "from": from_,
            "to": to,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateOrgUnit.parse_obj(data).org_unit_create

    async def _testing__create_employee(
        self, first_name: str, last_name: str
    ) -> TestingCreateEmployeeEmployeeCreate:
        query = gql(
            """
            mutation _Testing_CreateEmployee($first_name: String!, $last_name: String!) {
              employee_create(input: {given_name: $first_name, surname: $last_name}) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "first_name": first_name,
            "last_name": last_name,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateEmployee.parse_obj(data).employee_create

    async def _testing__create_address(
        self, person: UUID, value: str, address_type: UUID, from_: datetime
    ) -> TestingCreateAddressAddressCreate:
        query = gql(
            """
            mutation _Testing_CreateAddress($person: UUID!, $value: String!, $address_type: UUID!, $from: DateTime!) {
              address_create(
                input: {person: $person, value: $value, address_type: $address_type, validity: {from: $from}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "person": person,
            "value": value,
            "address_type": address_type,
            "from": from_,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateAddress.parse_obj(data).address_create

    async def _testing__create_org_unit_address(
        self, org_unit: UUID, value: str, address_type: UUID, from_: datetime
    ) -> TestingCreateOrgUnitAddressAddressCreate:
        query = gql(
            """
            mutation _Testing_CreateOrgUnitAddress($org_unit: UUID!, $value: String!, $address_type: UUID!, $from: DateTime!) {
              address_create(
                input: {org_unit: $org_unit, value: $value, address_type: $address_type, validity: {from: $from}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "org_unit": org_unit,
            "value": value,
            "address_type": address_type,
            "from": from_,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateOrgUnitAddress.parse_obj(data).address_create

    async def _testing__create_engagement(
        self,
        orgunit: UUID,
        person: UUID,
        engagement_type: UUID,
        job_function: UUID,
        from_: datetime,
    ) -> TestingCreateEngagementEngagementCreate:
        query = gql(
            """
            mutation _Testing_CreateEngagement($orgunit: UUID!, $person: UUID!, $engagement_type: UUID!, $job_function: UUID!, $from: DateTime!) {
              engagement_create(
                input: {org_unit: $orgunit, engagement_type: $engagement_type, job_function: $job_function, person: $person, validity: {from: $from}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "orgunit": orgunit,
            "person": person,
            "engagement_type": engagement_type,
            "job_function": job_function,
            "from": from_,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateEngagement.parse_obj(data).engagement_create

    async def _testing__create_manager(
        self,
        orgunit: UUID,
        manager_level: UUID,
        manager_type: UUID,
        responsibility: UUID,
        from_: datetime,
        person: UUID | None | UnsetType = UNSET,
        to: datetime | None | UnsetType = UNSET,
    ) -> TestingCreateManagerManagerCreate:
        query = gql(
            """
            mutation _Testing_CreateManager($orgunit: UUID!, $person: UUID, $manager_level: UUID!, $manager_type: UUID!, $responsibility: UUID!, $from: DateTime!, $to: DateTime) {
              manager_create(
                input: {org_unit: $orgunit, manager_level: $manager_level, manager_type: $manager_type, responsibility: [$responsibility], person: $person, validity: {from: $from, to: $to}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "orgunit": orgunit,
            "person": person,
            "manager_level": manager_level,
            "manager_type": manager_type,
            "responsibility": responsibility,
            "from": from_,
            "to": to,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateManager.parse_obj(data).manager_create

    async def _testing__update_manager(
        self,
        uuid: UUID,
        from_: datetime,
        to: datetime | None | UnsetType = UNSET,
        person: UUID | None | UnsetType = UNSET,
        user_key: str | None | UnsetType = UNSET,
    ) -> TestingUpdateManagerManagerUpdate:
        query = gql(
            """
            mutation _Testing_UpdateManager($uuid: UUID!, $from: DateTime!, $to: DateTime, $person: UUID, $user_key: String) {
              manager_update(
                input: {uuid: $uuid, validity: {from: $from, to: $to}, person: $person, user_key: $user_key}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "uuid": uuid,
            "from": from_,
            "to": to,
            "person": person,
            "user_key": user_key,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingUpdateManager.parse_obj(data).manager_update

    async def _testing__terminate_manager(
        self, uuid: UUID, to: datetime
    ) -> TestingTerminateManagerManagerTerminate:
        query = gql(
            """
            mutation _Testing_TerminateManager($uuid: UUID!, $to: DateTime!) {
              manager_terminate(input: {uuid: $uuid, to: $to}) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid, "to": to}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingTerminateManager.parse_obj(data).manager_terminate

    async def _testing__create_it_system(
        self, name: str, from_: datetime
    ) -> TestingCreateItSystemItsystemCreate:
        query = gql(
            """
            mutation _Testing_CreateItSystem($name: String!, $from: DateTime!) {
              itsystem_create(input: {user_key: $name, name: $name, validity: {from: $from}}) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"name": name, "from": from_}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateItSystem.parse_obj(data).itsystem_create

    async def _testing__create_it_user(
        self,
        itsystem: UUID,
        person: UUID,
        name: str,
        from_: datetime,
        engagements: list[UUID] | None | UnsetType = UNSET,
    ) -> TestingCreateItUserItuserCreate:
        query = gql(
            """
            mutation _Testing_CreateItUser($itsystem: UUID!, $person: UUID!, $name: String!, $from: DateTime!, $engagements: [UUID!]) {
              ituser_create(
                input: {user_key: $name, itsystem: $itsystem, person: $person, engagements: $engagements, validity: {from: $from}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "itsystem": itsystem,
            "person": person,
            "name": name,
            "from": from_,
            "engagements": engagements,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateItUser.parse_obj(data).ituser_create

    async def _testing__create_rolebinding(
        self, ituser: UUID, role: UUID, from_: datetime
    ) -> TestingCreateRolebindingRolebindingCreate:
        query = gql(
            """
            mutation _Testing_CreateRolebinding($ituser: UUID!, $role: UUID!, $from: DateTime!) {
              rolebinding_create(
                input: {ituser: $ituser, role: $role, validity: {from: $from}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"ituser": ituser, "role": role, "from": from_}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateRolebinding.parse_obj(data).rolebinding_create

    async def _testing__get_role_type(self) -> TestingGetRoleTypeFacets:
        query = gql(
            """
            query _Testing_GetRoleType {
              facets(filter: {user_keys: "role"}) {
                objects {
                  current {
                    classes {
                      uuid
                      name
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetRoleType.parse_obj(data).facets

    async def _testing__create_class(
        self, name: str, facet_uuid: UUID, from_: datetime
    ) -> TestingCreateClassClassCreate:
        query = gql(
            """
            mutation _Testing_CreateClass($name: String!, $facet_uuid: UUID!, $from: DateTime!) {
              class_create(
                input: {name: $name, user_key: $name, facet_uuid: $facet_uuid, validity: {from: $from}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "name": name,
            "facet_uuid": facet_uuid,
            "from": from_,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateClass.parse_obj(data).class_create

    async def _testing__get_role_facet(self) -> TestingGetRoleFacetFacets:
        query = gql(
            """
            query _Testing_GetRoleFacet {
              facets(filter: {user_keys: "role"}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetRoleFacet.parse_obj(data).facets

    async def _testing__get_related_units_for_org_unit(
        self, org_unit: UUID
    ) -> TestingGetRelatedUnitsForOrgUnitRelatedUnits:
        query = gql(
            """
            query _Testing_GetRelatedUnitsForOrgUnit($org_unit: UUID!) {
              related_units(filter: {org_unit: {uuids: [$org_unit]}}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"org_unit": org_unit}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetRelatedUnitsForOrgUnit.parse_obj(data).related_units

    async def _testing__terminate_org_unit(
        self, uuid: UUID, to: datetime
    ) -> TestingTerminateOrgUnitOrgUnitTerminate:
        query = gql(
            """
            mutation _Testing_TerminateOrgUnit($uuid: UUID!, $to: DateTime!) {
              org_unit_terminate(input: {uuid: $uuid, to: $to}) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid, "to": to}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingTerminateOrgUnit.parse_obj(data).org_unit_terminate

    async def _testing__create_related_units(
        self,
        origin: UUID,
        destination: list[UUID],
        from_: datetime,
        to: datetime | None | UnsetType = UNSET,
    ) -> TestingCreateRelatedUnitsRelatedUnitsUpdate:
        query = gql(
            """
            mutation _Testing_CreateRelatedUnits($origin: UUID!, $destination: [UUID!]!, $from: DateTime!, $to: DateTime) {
              related_units_update(
                input: {origin: $origin, destination: $destination, validity: {from: $from, to: $to}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "origin": origin,
            "destination": destination,
            "from": from_,
            "to": to,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateRelatedUnits.parse_obj(data).related_units_update
