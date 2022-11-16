from typing import Any
from functools import partial
from fastramqpi.context import Context
from gql import gql
from gql.client import AsyncClientSession
from pydantic import BaseModel
from strawberry.dataloader import DataLoader
from uuid import UUID


class Dataloader(BaseModel):
    """Collection of dataloaders"""

    class Config:
        """Arbitrary types need to be allowed in order to have Dataloader members"""

        arbitrary_types_allowed = True

    mo_user_loader: DataLoader
    mo_org_unit_loader: DataLoader


async def load_mo_user_data(
    uuids: list[UUID], graphql_session: AsyncClientSession
) -> dict[str, Any]:
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
              employees(uuids: %s) {
                objects {
                  name
                  addresses {
                    name
                    address_type {
                      name
                    }
                  }
                  cpr_no
                  engagements {
                    org_unit_uuid
                    org_unit {
                      name
                    }
                  }
                }
              }
            }
            """
            % [str(uuid) for uuid in uuids]
        ).replace(
            "'", '"'
        )  # Hack necessary, since graphql can't read single quotes
    )
    result = await graphql_session.execute(query)
    return result["employees"]


async def load_mo_org_unit_data(
    uuids: list[UUID], graphql_session: AsyncClientSession
) -> dict[str, Any]:
    """
    Loads a user's data

    Args:
        key: User UUID
        graphql_session: The GraphQL session to run queries on

    Return:
        Dictionary with queried user data
    """
    # print(uuids)
    # print("print([str(uuid) for uuid in uuids])")
    # print([str(uuid) for uuid in uuids])
    result = {}
    query = gql(
        (
            """
            query getData {
              org_units(uuids: %s) {
                objects {
                  managers {
                    employee_uuid
                    responsibilities {
                      name
                    }
                    manager_level {
                      name
                    }
                  }
                  name
                }
              }
            }   
            """
            % [str(uuid) for uuid in uuids]
        ).replace(
            "'", '"'
        )  # Hack necessary, since graphql can't read single quotes
    )
    result = await graphql_session.execute(query)
    # print(result)
    return result["org_units"]


def configure_dataloaders(context: Context) -> Dataloader:
    """
    Construct dataloaders based on FastRAMQPI context.

    Args:
        context: Context from FastRAMQPI

    Return:
        Relevant dataloaders
    """
    gql_loader_functions = {
        "mo_user_loader": load_mo_user_data,
        "mo_org_unit_loader": load_mo_org_unit_data,
    }

    graphql_session = context["user_context"]["gql_client"]
    gql_dataloaders = {
        key: DataLoader(
            load_fn=partial(value, graphql_session=graphql_session),
            cache=False,
        )
        for key, value in gql_loader_functions.items()
    }

    settings = context["user_context"]["settings"]

    return Dataloader(
        **gql_dataloaders,
    )
