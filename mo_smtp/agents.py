"""
Python file with agents that send emails
"""
from typing import Any

import structlog
from fastramqpi.context import Context
from ramqp.mo.models import PayloadType
from ramqp.utils import sleep_on_error

from .mail import EmailClient

logger = structlog.get_logger()


class Agents:
    def __init__(self, context: Context):
        self.dataloader = context["user_context"]["dataloader"]
        self.email_client = EmailClient(context)

    @sleep_on_error()
    async def inform_manager_on_employee_address_creation(
        self, payload: PayloadType, **kwargs: Any
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
        email_args: dict[str, Any] = {}

        # NOTE: New material
        address_data = await self.dataloader.load_mo_address_data(payload.object_uuid)

        # Sort out all employee.address.create messages, that aren't emails
        if address_data["address_type"]["scope"] != "EMAIL":
            logger.info("The address type is not EMAIL")
            return

        # Payload only includes user UUID. Query graphql to retrieve user data
        user_data = await self.dataloader.load_mo_user_data(payload.uuid)

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
