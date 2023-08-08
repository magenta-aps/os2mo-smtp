"""
Python file with agents that send emails
"""
import datetime
from typing import Annotated
from typing import Any

import structlog
from fastapi import Depends
from ramqp.depends import Context
from ramqp.depends import rate_limit
from ramqp.mo import MORouter
from ramqp.mo import PayloadUUID

from .config import AgentSettings

logger = structlog.get_logger()
delay_on_error = AgentSettings().delay_on_error
RateLimit = Annotated[None, Depends(rate_limit(delay_on_error))]

amqp_router = MORouter()


@amqp_router.register("address")
async def inform_manager_on_employee_address_creation(
    context: Context,
    uuid: PayloadUUID,
    _: RateLimit,
) -> None:
    """
    Listen to address creation events and inform the employee as well as his manager
    """
    logger.info(f"Obtained message with uuid = {uuid}")

    user_context = context["user_context"]
    dataloader = user_context["dataloader"]
    email_client = user_context["email_client"]

    # Prepare dictionary to store email arguments
    email_args: dict[str, Any] = {}

    address_data = await dataloader.load_mo_address_data(uuid)
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
) -> None:
    """
    Listen to manager events and inform `datagruppen` when a manager leaves the
    company

    Developed for Silkeborg Kommune
    """
    logger.info(f"Obtained message with uuid = {uuid}")

    user_context = context["user_context"]
    dataloader = user_context["dataloader"]
    email_client = user_context["email_client"]
    email_settings = user_context["email_settings"]

    # Load manager data from MO
    manager = await dataloader.load_mo_manager_data(uuid)
    to_date = manager["validity"]["to"]
    employee_uuid = manager["employee_uuid"]
    org_unit_uuid = manager["org_unit_uuid"]

    if not to_date:
        logger.info("Manager is currently employed. No message will be sent")
        return
    else:
        # Format the to-date as a datetime object at UTC+0
        to_datetime = datetime.datetime.fromisoformat(to_date).replace(tzinfo=None)
        logger.info(f"to-date (utc+0) = {to_datetime}")

    # Get the current time in UTC+0
    now = datetime.datetime.utcnow()
    logger.info(f"now (utc+0) = {now}")

    # Compare the to-date with the current time
    # Only send a mail if the to-date is in the past
    if to_datetime > now:
        logger.info("to_date is in the future. A mail will not be sent")
        return

    # Load employee data from MO
    if employee_uuid:
        employee = await dataloader.load_mo_user_data(employee_uuid)
    else:
        employee = {"name": "Unknown employee"}

    # Construct org unit location string
    org_unit = await dataloader.load_mo_org_unit_data(org_unit_uuid)
    location = await dataloader.get_org_unit_location(org_unit)

    # Write message
    message = f"""\
                    <html>
                    <head>
                    <style>
                    table {{
                        border-collapse: collapse;
                        }}
                    td, th {{
                      border: 1px solid #dddddd;
                      text-align: left;
                      padding: 8px;
                    }}
                    </style>
                    </head>
                      <body>
                        <p>
                           Denne besked er for at gøre opmærksom på, at
                           følgende medarbejder er blevet fjernet fra lederfanen
                           i OS2mo:
                           <br>
                           <br>
                           <table>
                             <tr>
                               <td>Navn:</td>
                               <td>{employee["name"]}</td>
                             </tr>
                             <tr>
                               <td>Slutdato på engagement:</td>
                               <td>{to_datetime.date()}</td>
                             </tr>
                             <tr>
                               <td>Placering:</td>
                               <td>{location}</td>
                             </tr>
                             <tr>
                               <td>Enhedsnummer:</td>
                               <td>{org_unit["user_key"]}</td>
                             </tr>
                           </table>
                           <br>

                           Med venlig hilsen,<br>
                           OS2mo
                           <br><br>
                           Denne besked kan ikke besvares.
                        </p>
                      </body>
                    </html>
                  """

    email_client.send_email(
        email_settings.receivers,
        "En medarbejder er blevet fjernet fra lederfanen",
        message,
        "html",
    )
