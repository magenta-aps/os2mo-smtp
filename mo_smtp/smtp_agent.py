# Opret en agent der modtager amqp-events og importerer og eksporterer til LDAP
#import asyncio
import structlog
from collections.abc import AsyncIterator
from typing import Any, Tuple
from contextlib import asynccontextmanager


from fastapi import FastAPI, APIRouter #, Query
from fastramqpi.main import FastRAMQPI
from raclients.graph.client import PersistentGraphQLClient
from raclients.modelclient.mo import ModelClient

from .config import Settings

# Possibly deprecated
# from ramqp import Router
# from ramqp.config import ConnectionSettings
from ramqp.mo import MORouter #, MOAMQPSystem

# from ramqp.mo.models import MORoutingKey
# from ramqp.mo.models import ObjectType
# from ramqp.mo.models import RequestType
# from ramqp.mo.models import ServiceType
from ramqp.mo.models import PayloadType

# from starlette.requests import Request


# Testing
from .send_email import send_email
from .dataloaders import configure_dataloaders
#from uuid import UUID


# help(MORouter)
# help(ServiceType)
# help(ObjectType)
# help(RequestType)

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

    #graphql_session = context["graphql_session"]
    #program_settings = context["user_context"]["settings"]

    # Prepare dictionary to store email arguments
    email_args = {}

    # Ignore all Create messages except the primary object
    # if not payload.uuid == payload.object_uuid:
    #    return

    # Payload only includes user UUID; query to graphql necessary to retreive user data
    user_data = (
        await context["user_context"]["dataloaders"].mo_user_loader.load_many(
            [payload.uuid]
        )
    )[0]["objects"][0]

    email_addresses = set(
        [
            address["name"]
            for address in user_data["addresses"]
            if address["address_type"]["name"] == "Email"
        ]
    )

    if email_addresses:
        email_args["receiver"] = email_addresses

    # If engagements (or possibly or_unit) is present, add manager's email to receive
    if user_data["engagements"]:
        org_unit_uuids = set()
        for engagement in user_data["engagements"]:
            org_unit_uuids.add(engagement["org_unit_uuid"])

        org_unit_data = await context["user_context"][
            "dataloaders"
        ].mo_org_unit_loader.load_many(list(org_unit_uuids))

        # Retrieve manager uuids from org_unit_data
        manager_uuids = set()
        for org_unit in org_unit_data:
            for obj in org_unit["objects"]:
                for manager in obj["managers"]:
                    manager_uuids.add(manager["employee_uuid"])

        manager_data = await context["user_context"][
            "dataloaders"
        ].mo_user_loader.load_many(list(manager_uuids))

        manager_emails = set()
        for manager in manager_data:
            manager_emails.update(
                [
                    address["name"]
                    for address in manager["objects"][0]["addresses"]
                    if address["address_type"]["name"] == "Email"
                ]
            )

        email_args["cc"] = list(manager_emails)

    # Generate subject string
    subject = "Registrering i MO"
    message_body = (
        "Denne besked er sendt som bekræftelse på at %s er oprettet i MO"
        % user_data["name"]
    )

    email_args["subject"] = subject
    email_args["body"] = message_body

    # Send email to relevant addresses
    await send_email(**email_args)

    # NOTE: Currently not working
    # Clear dataloader caches
    # context["user_context"]["dataloaders"].mo_user_loader.clear_all()
    # context["user_context"]["dataloaders"].mo_org_unit_loader.clear_all()

    return


for routing_key in Settings().routing_keys:
    amqp_router.register(routing_key)(listen_to_create)


@asynccontextmanager
async def seed_dataloaders(fastramqpi: FastRAMQPI) -> AsyncIterator[None]:
    """
    Seeding dataloaders by configuring them with current context.
    Adds dataloaders to FastRAMQPI instance

    Args:
        fastramqpi: running FastRAMQPI instance
    """

    logger.info("Seeding dataloaders")
    context = fastramqpi.get_context()
    dataloaders = configure_dataloaders(context)
    fastramqpi.add_context(dataloaders=dataloaders)
    yield


def construct_gql_client(settings: Settings):
    """
    GraphQLClient setup

    Args:
        settings: Settings from ./config.py file

    Return:
        GraphQL client
    """

    return PersistentGraphQLClient(
        url=settings.mo_url + "/graphql/v2",
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
    fastramqpi = FastRAMQPI(application_name="momail", settings=settings.fastramqpi)
    fastramqpi.add_context(settings=settings)

    logger.info("AMQP router setup")
    amqpsystem = fastramqpi.get_amqpsystem()
    amqpsystem.router.registry.update(amqp_router.registry)

    logger.info("Client setup")
    gql_client, model_client = construct_clients(settings)

    fastramqpi.add_context(model_client=model_client)
    fastramqpi.add_context(gql_client=gql_client)

    fastramqpi.add_lifespan_manager(seed_dataloaders(fastramqpi), 2000)

    logger.info("Configuring dataloaders")
    context = fastramqpi.get_context()
    dataloaders = configure_dataloaders(context)
    fastramqpi.add_context(dataloaders=dataloaders)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    return fastramqpi


def create_app(**kwargs: Any) -> FastAPI:
    fastramqpi = create_fastramqpi(**kwargs)
    return fastramqpi.get_app()
