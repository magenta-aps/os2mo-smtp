from typing import Any
from uuid import UUID

from gql import gql
from gql.client import AsyncClientSession


async def load_mo_user_data(uuid: UUID, graphql_session: AsyncClientSession) -> Any:
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
    result = await graphql_session.execute(query)
    return result["employees"][0]["objects"][0]


async def load_mo_org_unit_data(uuid: UUID, graphql_session: AsyncClientSession) -> Any:
    """
    Loads a user's data

    Args:
        key: User UUID
        graphql_session: The GraphQL session to run queries on

    Return:
        Dictionary with queried user data
    """
    query = gql(
        (
            """
            query getData {
              org_units(uuids: "%s") {
                objects {
                  name
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
    result = await graphql_session.execute(query)
    return result["org_units"][0]["objects"][0]
