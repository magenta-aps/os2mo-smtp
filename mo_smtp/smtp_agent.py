from typing import Any
from typing import Tuple

import structlog
from fastapi import APIRouter
from fastapi import FastAPI
from fastramqpi.main import FastRAMQPI
from raclients.graph.client import PersistentGraphQLClient
from raclients.modelclient.mo import ModelClient
from ramqp.mo import MORouter

from .agents import Agents
from .config import EmailSettings
from .config import Settings
from .dataloaders import DataLoader

logger = structlog.get_logger()
amqp_router = MORouter()
fastapi_router = APIRouter()


def register_agents(agents, agents_to_register):
    """
    Register agents so they listen to AMQP messages
    """
    for agent_to_register in agents_to_register:
        logger.info(f"Activating {agent_to_register}")
        agent = getattr(agents, agent_to_register)
        amqp_router.register("*.*.*")(agent)


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
    email_settings = EmailSettings(**kwargs)

    logger.info("FastRAMQPI setup")
    fastramqpi = FastRAMQPI(
        application_name=settings.application_name, settings=settings.fastramqpi
    )
    fastramqpi.add_context(settings=settings)
    fastramqpi.add_context(email_settings=email_settings)

    logger.info("Client setup")
    gql_client, model_client = construct_clients(settings)

    fastramqpi.add_context(model_client=model_client)
    fastramqpi.add_context(gql_client=gql_client)

    logger.info("Initializing dataloaders")
    dataloader = DataLoader(fastramqpi.get_context())
    fastramqpi.add_context(dataloader=dataloader)

    logger.info("AMQP router setup")
    amqpsystem = fastramqpi.get_amqpsystem()
    register_agents(Agents(fastramqpi.get_context()), settings.active_agents)
    amqpsystem.router.registry.update(amqp_router.registry)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    return fastramqpi


def create_app(**kwargs: Any) -> FastAPI:
    fastramqpi = create_fastramqpi(**kwargs)
    return fastramqpi.get_app()
