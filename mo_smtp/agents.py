"""
Python file with agents that send emails
"""

import datetime
import os
from typing import Any

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
from .dataloaders import DataLoader
from .dataloaders import get_org_unit_relations
from .dataloaders import get_institution_address

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
    dataloader = DataLoader(mo)

    # Prepare dictionary to store email arguments
    email_args: dict[str, Any] = {}

    address_data = await dataloader.load_mo_address_data(uuid)

    if not address_data:
        logger.info("Address not found")
        return

    employee_uuid = address_data["employee_uuid"]

    if not employee_uuid:
        logger.info("The address does not belong to an employee")
        return

    # Sort out all 'address' messages, that aren't emails
    if address_data["address_type"]["scope"] != "EMAIL":
        logger.info("The address type is not EMAIL")
        return

    user_data = await dataloader.load_mo_user_data(employee_uuid)

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
    email_addresses = {
        address["value"]
        for address in user_data["addresses"]
        if address["address_type"]["scope"] == "EMAIL"
        and "@" in address["value"]  # Rudimentary email validator
    }
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
            await dataloader.load_mo_org_unit_data(uuid)
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
            if not manager_uuid:
                continue
            manager = await dataloader.load_mo_user_data(manager_uuid)
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
    dataloader = DataLoader(mo)

    # Load manager data from MO
    manager = await dataloader.load_mo_manager_data(uuid)
    if not manager:
        logger.info("Manager not found")
        return

    to_date = manager["validity"]["to"]
    employee_uuid = manager["employee_uuid"]
    org_unit_uuid = manager["org_unit_uuid"]

    if not to_date and employee_uuid:
        logger.info("Manager is currently employed. No message will be sent")
        return
    elif not to_date and not employee_uuid:  # vacant manager
        from_date = manager["validity"]["from_"]
        # Insert from_date in `to_datetime`, as a vacant from_date equals a terminated manager's to_date
        to_datetime = from_date.replace(tzinfo=None)
        template = load_template("alert_on_vacant_manager.html")
        logger.info("Vacant from (utc+0): ", datetime=to_datetime)
    else:  # terminated manager
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
        employee = await dataloader.load_mo_user_data(employee_uuid)
    else:
        employee = {"name": "Vacant manager"}

    # Construct org unit location string
    org_unit = await dataloader.load_mo_org_unit_data(org_unit_uuid)
    location = await dataloader.get_org_unit_location(org_unit)

    context = {
        "name": employee["name"],
        "to_date": to_datetime.date(),
        "location": location,
        "user_key": org_unit["user_key"],
    }

    message = template.render(context=context)

    email_client.send_email(
        email_settings.receivers,
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
            if one(one(relation.org_units).root).uuid != root:
                logger.info("Org unit has a relation outside of the Lønorganisation")
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
