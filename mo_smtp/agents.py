"""
Python file with agents that send emails
"""

import datetime
import os
from uuid import UUID
from typing import Any

from mo_smtp.autogenerated_graphql_client.employee_name import (
    EmployeeNameEmployeesObjectsCurrent,
)
import structlog
from fastramqpi.ramqp.depends import Context
from fastramqpi.ramqp.depends import RateLimit
from fastramqpi.ramqp.mo import MORouter
from fastramqpi.ramqp.mo import PayloadUUID
from jinja2 import Environment
from jinja2 import FileSystemLoader
from more_itertools import one

from . import depends
from .depends import Settings
from .dataloaders import (
    get_address_data,
    get_employee_data,
    get_employee_name,
    get_manager_data,
    get_org_unit_data,
    get_org_unit_location,
)
from .dataloaders import get_org_unit_relations
from .dataloaders import get_institution_address
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
    context: Context,
    uuid: PayloadUUID,
    _: RateLimit,
    mo: depends.GraphQLClient,
) -> None:
    """
    Listen to manager events and inform `datagruppen` when a manager leaves the
    company

    Developed for Silkeborg Kommune
    """
    logger.info("Listening on a manager event with uuid:", uuid=uuid)

    user_context = context["user_context"]
    email_client = user_context["email_client"]
    email_settings = user_context["email_settings"]

    # Load manager data from MO
    manager = await get_manager_data(mo, uuid)
    if not manager:
        logger.info("Manager not found")
        return

    to_date = manager.validity.to
    employee_uuid = manager.employee_uuid
    org_unit_uuid = manager.org_unit_uuid

    if not to_date and employee_uuid:
        logger.info("Manager is currently employed. No message will be sent")
        return
    elif not to_date and not employee_uuid:  # branch for vacant manager object
        from_date = manager.validity.from_
        # Insert from_date in `to_datetime`, as a vacant from_date equals a terminated manager's to_date
        to_datetime = from_date.replace(tzinfo=None)
        template = load_template("alert_on_vacant_manager.html")
        logger.info("Vacant from (utc+0): ", datetime=to_datetime)
    else:  # branch for terminated manager object
        # Format the to-date as a datetime object at UTC+0
        to_datetime = to_date.replace(tzinfo=None)
        template = load_template("alert_on_manager_termination.html")
        logger.info("Terminate from(utc+0): ", datetime=to_datetime)

    # Get the current time in UTC+0
    now = datetime.datetime.utcnow()
    logger.info("Now (utc+0): ", now=now)

    # Compare the to-date with the current time
    # Only send a mail if the to-date is in the past
    if to_datetime > now:
        logger.info("to_date is in the future. A mail will not be sent")
        return

    # Load employee data from MO
    if employee_uuid:
        employee = await get_employee_name(mo, employee_uuid)
    else:
        employee = EmployeeNameEmployeesObjectsCurrent.parse_obj(
            {"name": "Vacant manager"}
        )

    # Construct org unit location string
    org_unit = await get_org_unit_data(mo, org_unit_uuid)
    if not org_unit:
        logger.info(
            "Org unit is possibly terminated or doesn't exist. An email will not be sent"
        )
        return

    location = await get_org_unit_location(mo, org_unit_uuid)

    context = {
        "name": employee.name,
        "to_date": to_datetime.date(),
        "location": location,
        "user_key": org_unit.user_key,
    }

    message = template.render(context=context)

    settings = Settings()
    if settings.alert_manager_removal_use_org_unit_emails:
        receivers = await get_institution_address(
            mo, org_unit_uuid, one(org_unit.root).uuid
        )
    else:
        receivers = set(email_settings.receivers)

    email_client.send_email(
        receivers,
        "En medarbejder er blevet fjernet fra lederfanen",
        message,
        "html",
    )


@amqp_router.register("org_unit")
async def alert_on_org_unit_without_relation(
    context: Context,
    uuid: PayloadUUID,
    _: RateLimit,
    mo: depends.GraphQLClient,
) -> None:
    logger.info("Obtained message", uuid=str(uuid))

    settings = Settings()
    assert settings.root_loen_org
    root = settings.root_loen_org

    org_unit_data = await get_org_unit_relations(mo, org_unit_uuid=uuid)

    # Load manager data from MO
    if not org_unit_data:
        logger.info("Org unit not found")
        return

    current = one(org_unit_data).current
    if one(current.root).uuid != root:
        logger.info("Org unit is not in the Lønorganisation")
        return

    if current.related_units:
        for relation in current.related_units:
            for org_unit in relation.org_units:
                if one(org_unit.root).uuid != root:
                    logger.info(
                        "Org unit has a relation outside of the Lønorganisation"
                    )
                    return

    # get_address
    emails = await get_institution_address(mo, uuid, root)

    user_context = context["user_context"]
    email_client = user_context["email_client"]

    # Prepare dictionary to store email arguments
    email_args: dict[str, Any] = {}

    email_args["receiver"] = emails

    # Subject string
    subject = "Manglende relation i Lønorganisation"
    message_body = (
        "Denne besked er sendt som en påmindelse om at "
        + f"enheden: {current.name} "
        + "ikke er relateret til en enhed i Administrationsorganisationen."
    )
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
