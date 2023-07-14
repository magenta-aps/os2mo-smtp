"""
Python file with agents that send emails
"""
from typing import Annotated
from typing import Any

import structlog
from fastapi import Depends
from ramqp.depends import Context
from ramqp.depends import rate_limit
from ramqp.mo import PayloadUUID

from .config import AgentSettings

logger = structlog.get_logger()
delay_on_error = AgentSettings().delay_on_error
RateLimit = Annotated[None, Depends(rate_limit(delay_on_error))]


class Agents:
    def __init__(self, context: Context):
        user_context = context["user_context"]
        self.dataloader = user_context["dataloader"]
        self.email_client = user_context["email_client"]

    async def inform_manager_on_employee_address_creation(
        self,
        uuid: PayloadUUID,
        _: RateLimit,
    ) -> None:
        """
        Listen to address creation events and inform the employee as well as his manager
        """
        logger.info(f"Obtained message with uuid = {uuid}")

        # Prepare dictionary to store email arguments
        email_args: dict[str, Any] = {}

        address_data = await self.dataloader.load_mo_address_data(uuid)
        employee_uuid = address_data["employee_uuid"]

        if not employee_uuid:
            logger.info("The address does not belong to an employee")
            return

        # Sort out all 'address' messages, that aren't emails
        if address_data["address_type"]["scope"] != "EMAIL":
            logger.info("The address type is not EMAIL")
            return

        user_data = await self.dataloader.load_mo_user_data(employee_uuid)

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
                await self.dataloader.load_mo_org_unit_data(uuid)
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
                manager = await self.dataloader.load_mo_user_data(manager_uuid)
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
        self.email_client.send_email(**email_args)
