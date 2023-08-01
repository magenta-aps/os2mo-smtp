from typing import Any
from uuid import UUID

from fastramqpi.context import Context
from gql import gql


class DataLoader:
    def __init__(self, context: Context):
        self.gql_client = context["user_context"]["gql_client"]

    async def load_mo_manager_data(self, uuid: UUID) -> Any:
        query = gql(
            """
            query getManagerData {
              managers(
                  uuids: "%s",
                  from_date: "1900-01-01"
                  to_date: "5000-01-01"
              ) {
                objects {
                  employee_uuid
                  org_unit_uuid
                  validity {
                    to
                  }
                }
              }
            }
            """
            % uuid
        )

        result = await self.gql_client.execute(query)
        return result["managers"][0]["objects"][0]

    async def load_mo_user_data(self, uuid: UUID) -> Any:
        """
        Loads a user's data

        Args:
            uuids: List of user UUIDs to query
            graphql_session: The GraphQL session to run queries on

        Return:
            Dictionary with queried user data
        """

        query = gql(
            (
                """
                query getData {
                  employees(uuids: "%s") {
                    objects {
                      name
                      addresses {
                        value
                        address_type {
                          scope
                        }
                      }
                      engagements {
                        org_unit_uuid
                      }
                    }
                  }
                }
                """
                % uuid
            )
        )
        result = await self.gql_client.execute(query)
        return result["employees"][0]["objects"][0]

    async def load_mo_root_org_uuid(self):
        query = gql(
            (
                """
                query getData {
                  org {
                    uuid
                  }
                }
                """
            )
        )
        result = await self.gql_client.execute(query)
        return result["org"]["uuid"]

    async def load_mo_org_unit_data(self, uuid: UUID) -> Any:
        """
        Loads a user's data

        Args:
            key: User UUID
            graphql_session: The GraphQL session to run queries on

        Return:
            Dictionary with queried org unit data
        """
        query = gql(
            (
                """
                query getData {
                  org_units(uuids: "%s") {
                    objects {
                      name
                      user_key
                      parent_uuid
                      managers {
                        employee_uuid
                      }
                    }
                  }
                }
                """
                % uuid
            )
        )
        result = await self.gql_client.execute(query)
        return result["org_units"][0]["objects"][0]

    async def load_mo_address_data(self, uuid: UUID) -> Any:
        """
        Loads information concerning an employee's address

        Args:
            key: User UUID
            graphql_session: The GraphQL session to run queries on

        Return:
            Dictionary with queried address data
        """
        query = gql(
            (
                """
                query getData {
                  addresses(uuids: "%s") {
                    current {
                      name
                      employee_uuid
                      address_type {
                        scope
                      }
                    }
                  }
                }
                """
                % uuid
            )
        )
        result = await self.gql_client.execute(query)
        return result["addresses"][0]["current"]

    async def get_org_unit_location(self, org_unit):
        """
        Constructs and org-unit location string, where different org-units in the
        hierarchy are separated by forward slashes.
        """
        root_org_uuid = await self.load_mo_root_org_uuid()
        org_unit_location = org_unit["name"]
        parent_uuid = org_unit["parent_uuid"]

        # do not include the root-org unit in the location string
        while parent_uuid != root_org_uuid:
            parent = await self.load_mo_org_unit_data(parent_uuid)
            parent_uuid = parent["parent_uuid"]
            org_unit_location = parent["name"] + " / " + org_unit_location

        return org_unit_location
