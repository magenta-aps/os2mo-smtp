# Opret en agent der modtager amqp-events og importerer og eksporterer til LDAP
from typing import Any
from typing import Tuple

import structlog
from fastapi import APIRouter
from fastapi import FastAPI
from fastramqpi.main import FastRAMQPI
from raclients.graph.client import PersistentGraphQLClient
from raclients.modelclient.mo import ModelClient
from ramqp.mo import MORouter
from ramqp.mo.models import PayloadType
from ramqp.utils import RejectMessage

from .config import EmailSettings
from .config import RoutingKeys
from .config import Settings
from .dataloaders import load_mo_org_unit_data
from .dataloaders import load_mo_user_data
from .send_email import send_email


logger = structlog.get_logger()
amqp_router = MORouter()
fastapi_router = APIRouter()


async def listen_to_create(context: dict, payload: PayloadType, **kwargs: Any) -> None:
    """
    Create a router, which listens to all "creation" requests,
    takes a context and a payload, and returns None.
    In time, it may be wise to limit the input to more specfic creation events,
    but that is a problem for another time

    Args:
        context: dictionary with context from FastRAMQPI
        payload: Payload of the AMQP message
    """

    # Prepare dictionary to store email arguments
    # NOTE: Use and assignments too dynamic for mypy, so Any-hint used as workaround
    email_args: dict[str, Any] = dict(EmailSettings())
    gql_client = context["user_context"]["gql_client"]

    # Payload only includes user UUID. Query to graphql necessary to retreive user data
    user_data = (await load_mo_user_data([payload.uuid], gql_client,))[0][
        "objects"
    ][0]
    # Subject string
    subject = "Registrering i MO"
    message_body = (
        f"Denne besked er sendt som bekræftelse på at {user_data['name']} "
        + "er registreret i "
    )
    try:
        email_addresses = set(
            [
                address["value"]
                for address in user_data["addresses"]
                if address["address_type"]["scope"] == "EMAIL"
            ]
        )
    except KeyError:
        raise RejectMessage(f"User {user_data['name']} does not have an email")
        return

    email_args["receiver"] = email_addresses

    # If engagements is present, add manager's email to receive
    if user_data["engagements"]:
        org_unit_uuids = set()
        for engagement in user_data["engagements"]:
            org_unit_uuids.add(engagement["org_unit_uuid"])
        org_unit_data = await load_mo_org_unit_data(list(org_unit_uuids), gql_client)

        # Add units to message body
        if len(org_unit_data) > 1:
            message_body += "de følgende enheder:\n"
            for org_unit in org_unit_data[:-1]:
                message_body += org_unit["objects"][0]["name"] + ",\n"
        message_body += org_unit_data[-1]["objects"][0]["name"]

        # Retrieve manager uuids from org_unit_data
        manager_uuids = set()
        for org_unit in org_unit_data:
            for obj in org_unit["objects"]:
                for manager in obj["managers"]:
                    manager_uuids.add(manager["employee_uuid"])

        manager_data = await load_mo_user_data(list(manager_uuids), gql_client)

        manager_emails = set()
        for manager in manager_data:
            manager_emails.update(
                [
                    address["value"]
                    for address in manager["objects"][0]["addresses"]
                    if address["address_type"]["scope"] == "EMAIL"
                ]
            )

        email_args["cc"] = manager_emails

    email_args["subject"] = subject
    email_args["body"] = message_body

    # Send email to relevant addresses
    await send_email(**email_args)


def update_amqp_router_registry(routing_keys: dict[str, str]):
    for routing_key in routing_keys:
        amqp_router.register(routing_keys[routing_key])(listen_to_create)


def construct_gql_client(settings: Settings):
    """
    GraphQLClient setup

    Args:
        settings: Settings from ./config.py file

    Return:
        GraphQL client
    """

    return PersistentGraphQLClient(
        url=settings.mo_url + "/graphql/v3",
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
        auth_server=settings.auth_server,
        auth_realm=settings.auth_realm,
        execute_timeout=settings.graphql_timeout,
        httpx_client_kwargs={"timeout": settings.graphql_timeout},
    )


def construct_model_client(settings: Settings):
    """
    MO client setup

    Args:
        settings: Settings from ./config.py file

    Return:
        MO client
    """
    return ModelClient(
        base_url=settings.mo_url,
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
        auth_server=settings.auth_server,
        auth_realm=settings.auth_realm,
    )


def construct_clients(
    settings: Settings,
) -> Tuple[PersistentGraphQLClient, ModelClient]:
    """
    Construct clients from settings found in ./config.py

    Args:
        settings: Settings from ./config.py file
    """

    gql_client = construct_gql_client(settings)
    model_client = construct_model_client(settings)
    return gql_client, model_client


def create_fastramqpi(**kwargs: Any) -> FastRAMQPI:
    """
    Initiate a FastRAMQPI instance.
    """

    logger.info("Import settings")
    settings = Settings(**kwargs)

    logger.info("FastRAMQPI setup")
    fastramqpi = FastRAMQPI(
        application_name=settings.application_name, settings=settings.fastramqpi
    )
    fastramqpi.add_context(settings=settings)

    logger.info("AMQP router setup")
    amqpsystem = fastramqpi.get_amqpsystem()
    update_amqp_router_registry(RoutingKeys().dict())
    amqpsystem.router.registry.update(amqp_router.registry)

    logger.info("Client setup")
    gql_client, model_client = construct_clients(settings)

    fastramqpi.add_context(model_client=model_client)
    fastramqpi.add_context(gql_client=gql_client)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    return fastramqpi


def create_app(**kwargs: Any) -> FastAPI:
    fastramqpi = create_fastramqpi(**kwargs)
    return fastramqpi.get_app()
