# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os
from uuid import UUID
from typing import Any

import structlog
from fastramqpi.ramqp.depends import Context
from fastramqpi.ramqp.depends import RateLimit
from fastramqpi.ramqp.mo import MORouter
from fastramqpi.ramqp.mo import PayloadUUID
from jinja2 import Environment
from jinja2 import FileSystemLoader
from more_itertools import one

from mo_smtp.dataloaders import fetch_notifications_from_db
from mo_smtp.helpers import get_manager_end_date
from mo_smtp import depends
from .dataloaders import (
    get_address_data,
    get_employee_data,
)
from .dataloaders import get_ituser_uuid_by_rolebinding
from .dataloaders import get_ituser

logger = structlog.get_logger()

amqp_router = MORouter()


def load_template(filename):
    templates_folder = os.path.join(os.path.dirname(__file__), "email_templates")
    file_loader = FileSystemLoader(templates_folder)
    env = Environment(loader=file_loader)
    template = env.get_template(filename)

    return template


@amqp_router.register("address")
async def inform_manager_on_employee_address_creation(
    context: Context,
    uuid: PayloadUUID,
    _: RateLimit,
    mo: depends.GraphQLClient,
) -> None:
    """
    Listen to address creation events and inform the employee as well as his manager
    """
    logger.info(f"Obtained message with uuid = {uuid}")

    user_context = context["user_context"]
    email_client = user_context["email_client"]

    # Prepare dictionary to store email arguments
    email_args: dict[str, Any] = {}

    address_data = await get_address_data(mo, uuid)

    if not address_data:
        logger.info("Address not found")
        return

    employee_uuid = address_data.employee_uuid

    if not employee_uuid:
        logger.info("The address does not belong to an employee")
        return

    # Sort out all 'address' messages, that aren't emails
    if address_data.address_type.scope != "EMAIL":
        logger.info("The address type is not EMAIL")
        return

    employee_data = await get_employee_data(mo, employee_uuid)

    emails = {address.value for address in employee_data.addresses}

    # Drop message, if previous email exists
    if len(emails) > 1:
        logger.info("A previous email address exists")
        return

    # Subject string
    subject = "Registrering i MO"
    message_body = (
        f"Denne besked er sendt som bekræftelse på at {employee_data.name} "
        + "er registreret i "
    )

    email_args["receiver"] = emails

    # If engagements are present, add manager's email to receive
    if employee_data.engagements:
        org_unit_names = set()
        manager_emails = set()

        for engagement in employee_data.engagements:
            org_unit_names.add(one(engagement.org_unit).name)

            for manager in engagement.managers:
                for address in one(manager.person).addresses:
                    manager_emails.add(address.value)

        # Add units to message body
        if len(org_unit_names) > 1:
            message_body += "de følgende enheder:\n" + ",\n".join(org_unit_names)
        else:
            message_body += next(iter(org_unit_names))

        email_args["cc"] = manager_emails
    else:
        message_body += "OS2MO."

    email_args["subject"] = subject
    email_args["body"] = message_body
    email_args["texttype"] = "plain"

    # Send email to relevant addresses
    email_client.send_email(**email_args)


@amqp_router.register("manager")
async def alert_on_manager_removal(
    manager_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    session: depends.Session,
    _: RateLimit,
) -> None:
    """
    Listen to manager events and inform `datagruppen` when a manager leaves the
    company

    Developed for Silkeborg Kommune
    """
    logger.info("Listening on a manager event with uuid:", uuid=manager_uuid)

    # Load manager data from MO
    # TODO: This needs to handle `from/to` for employee and org_unit, in case there's history
    result = await mo.get_manager(manager_uuid)
    if len(result.objects) == 0 or one(result.objects).validities is None:
        logger.info("Manager not found")
        return

    manager = one(result.objects).validities
    relevant_manager = get_manager_end_date(manager)

    if not relevant_manager:
        logger.info(
            "No relevant manager validity found for uuid:", uuid=str(manager_uuid)
        )
        return

    db_notification = await fetch_notifications_from_db(session, manager_uuid)
    if db_notification:
        if db_notification == relevant_manager:
            logger.info(
                "Notification already exists for manager with uuid:",
                uuid=str(manager_uuid),
            )
            return

        await session.delete(db_notification)
        logger.info("Delete old notification for manager", uuid=str(manager_uuid))

    session.add(relevant_manager)
    logger.info("Created new notification for manager", uuid=str(manager_uuid))
    return


@amqp_router.register("org_unit")
async def alert_on_org_unit_without_relation(
    org_unit_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    session: depends.Session,
    _: RateLimit,
) -> None:
    logger.info("Listening on an org_unit event with uuid:", uuid=org_unit_uuid)

    assert settings.root_loen_org
    root = settings.root_loen_org

    result = await mo.get_org_unit_relations(mo, org_unit_uuid=org_unit_uuid)
    if len(result.objects) == 0 or one(result.objects).validities is None:
        logger.info("Org unit not found")
        return

    org_unit = one(result.objects).validities
    if org_unit.root.uuid != root:
        logger.info("Org unit is not in the Lønorganisation")
        return

    if org_unit.related_units:
        for relation in org_unit.related_units:
            for unit in relation.org_units:
                if one(unit.root).uuid != root:
                    logger.info(
                        "Org unit has a relation outside of the Lønorganisation"
                    )
                    return

    # get_address

    user_context = context["user_context"]
    email_client = user_context["email_client"]

    # Prepare dictionary to store email arguments
    email_args: dict[str, Any] = {}

    email_args["receiver"] = emails

    # Subject string
    email_args["subject"] = subject
    email_args["body"] = message_body
    email_args["texttype"] = "plain"

    # Send email to relevant addresses
    email_client.send_email(**email_args)


# TODO: This should be stored in a db, since a restart would throw away the last message
_last_sent_messages: dict = {}


@amqp_router.register("rolebinding")  # type: ignore
async def alert_on_rolebinding(
    context: Context,
    uuid: PayloadUUID,
    _: RateLimit,
    mo: depends.GraphQLClient,
) -> None:
    ituser_uuid = await get_ituser_uuid_by_rolebinding(mo, uuid=uuid)
    if not ituser_uuid:
        logger.info(
            "IT-user is possibly terminated or doesn't exist. An email will not be sent"
        )
        return None
    return await generate_ituser_email(context, ituser_uuid, mo)


@amqp_router.register("ituser")
async def alert_on_ituser(
    context: Context,
    uuid: PayloadUUID,
    _: RateLimit,
    mo: depends.GraphQLClient,
) -> None:
    return await generate_ituser_email(context, uuid, mo)


async def generate_ituser_email(
    context: Context,
    ituser_uuid: UUID,
    mo: depends.GraphQLClient,
) -> None:
    user_context = context["user_context"]
    email_client = user_context["email_client"]
    email_settings = user_context["email_settings"]

    ituser = await get_ituser(mo, uuid=ituser_uuid)
    if not ituser:
        logger.info(
            "IT-user is possibly terminated or doesn't exist. An email will not be sent"
        )
        return

    rolebindings = ituser.rolebindings
    itsystem = ituser.itsystem.name
    person = one(ituser.person).name if ituser.person else None
    roles = [one(rb.role) for rb in rolebindings]

    template = load_template("alert_on_rolebinding.html")

    context = {
        "person": person,
        "ituser": ituser.user_key,
        "itsystem": itsystem,
        "roles": roles,
    }

    if context == _last_sent_messages.get(ituser_uuid):
        logger.info("Email is identical to the previous. An email will not be sent")
        return

    message = template.render(context=context)

    email_client.send_email(
        set(email_settings.receivers),
        "En IT-bruger er blevet oprettet i MO",
        message,
        "html",
    )
    _last_sent_messages[ituser_uuid] = context
