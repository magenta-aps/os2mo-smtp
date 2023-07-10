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
from ramqp.utils import sleep_on_error

from .config import EmailSettings
from .config import Settings
from .dataloaders import load_mo_address_data
from .dataloaders import load_mo_org_unit_data
from .dataloaders import load_mo_user_data
from .send_email import send_email


logger = structlog.get_logger()
amqp_router = MORouter()
fastapi_router = APIRouter()


@sleep_on_error()
async def listen_to_address_create(
    context: dict, payload: PayloadType, **kwargs: Any
) -> None:
    """
    Create a router, which listens to all "creation" requests,
    takes a context and a payload, and returns None.
    In time, it may be wise to limit the input to more specfic creation events,
    but that is a problem for another time

    Args:
        context: dictionary with context from FastRAMQPI
        payload: Payload of the AMQP message
    """
    routing_key = kwargs["mo_routing_key"]
    routing_key_str = str(routing_key)
    logger.info(f"Obtained message with routing key = {routing_key_str}")

    if routing_key_str != "employee.address.create":
        logger.info("Only listening to 'employee.address.create'")
        return

    # When a new employee is created, the AMPQ request corresponds with that of an
    # address but the payload.object_uuid is always equal to the payload.uuid
    if payload.uuid == payload.object_uuid:
        logger.info("payload uuid equals object uuid")
        return

    # Prepare dictionary to store email arguments
    # NOTE: Use and assignments too dynamic for mypy, so Any-hint used as workaround
    email_args: dict[str, Any] = dict(EmailSettings())
    gql_client = context["user_context"]["gql_client"]

    # NOTE: New material
    address_data = await load_mo_address_data(payload.object_uuid, gql_client)

    # Sort out all employee.address.create messages, that aren't emails
    if address_data["address_type"]["scope"] != "EMAIL":
        logger.info("The address type is not EMAIL")
        return

    # Payload only includes user UUID. Query to graphql necessary to retreive user data
    user_data = await load_mo_user_data(payload.uuid, gql_client)

    emails = [
        email
        for email in user_data["addresses"]
        if email["address_type"]["scope"] == "EMAIL"
    ]
    # Drop message, if previous email exists
    if len(emails) > 1:
        logger.info("A previous email address exists")
        return

    # Subject string
    subject = "Registrering i MO"
    message_body = (
        f"Denne besked er sendt som bekræftelse på at {user_data['name']} "
        + "er registreret i "
    )
    email_addresses = set(
        [
            address["value"]
            for address in user_data["addresses"]
            if address["address_type"]["scope"] == "EMAIL"
            and "@" in address["value"]  # Rudimentary email validator
        ]
    )
    # Sometimes invalid emails may be imported from AD.
    if not email_addresses:
        logger.info(f"User {user_data['name']} does not have an email")
        return

    email_args["receiver"] = email_addresses

    # If engagements are present, add manager's email to receive
    if user_data["engagements"]:
        org_unit_uuids = set()
        for engagement in user_data["engagements"]:
            org_unit_uuids.add(engagement["org_unit_uuid"])

        org_unit_data = [
            await load_mo_org_unit_data(uuid, gql_client)
            for uuid in list(org_unit_uuids)
        ]

        # Add units to message body
        if len(org_unit_data) > 1:
            message_body += "de følgende enheder:\n"
            for org_unit in org_unit_data[:-1]:
                message_body += org_unit["name"] + ",\n"
        message_body += org_unit_data[-1]["name"]

        # Retrieve manager uuids from org_unit_data
        manager_uuids = set()
        for obj in org_unit_data:
            for manager in obj["managers"]:
                manager_uuids.add(manager["employee_uuid"])

        manager_emails = set()
        for manager_uuid in manager_uuids:
            manager = await load_mo_user_data(manager_uuid, gql_client)
            manager_emails.update(
                [
                    address["value"]
                    for address in manager["addresses"]
                    if address["address_type"]["scope"] == "EMAIL"
                ]
            )

        email_args["cc"] = manager_emails
    else:
        message_body += "OS2MO."

    email_args["subject"] = subject
    email_args["body"] = message_body

    # Send email to relevant addresses
    send_email(**email_args)


def update_amqp_router_registry():
    amqp_router.register("*.*.*")(listen_to_address_create)


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
    update_amqp_router_registry()
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
