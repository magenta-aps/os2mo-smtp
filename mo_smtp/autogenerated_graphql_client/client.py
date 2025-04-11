from uuid import UUID

from .address_data import AddressData, AddressDataAddresses
from .async_base_client import AsyncBaseClient
from .employee_data import EmployeeData, EmployeeDataEmployees
from .employee_name import EmployeeName, EmployeeNameEmployees
from .institution_address import InstitutionAddress, InstitutionAddressOrgUnits
from .ituser import Ituser, ItuserItusers
from .manager_data import ManagerData, ManagerDataManagers
from .org_unit_ancestors import OrgUnitAncestors, OrgUnitAncestorsOrgUnits
from .org_unit_data import OrgUnitData, OrgUnitDataOrgUnits
from .org_unit_relations import OrgUnitRelations, OrgUnitRelationsOrgUnits
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
