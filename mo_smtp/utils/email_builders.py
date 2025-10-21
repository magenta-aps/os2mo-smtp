# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from email.message import EmailMessage

from mo_smtp import depends
from mo_smtp.models import ManagerNotification
# from mo_smtp.models import OrgUnitNotification


async def build_manager_email(
    notification: ManagerNotification,
    mo: depends.GraphQLClient,
    settings: depends.Settings,
) -> EmailMessage:
    # Pseudo
    data = mo.get_some_data(notification.employee_uuid)
    name = data.person.name
    org_unit_user_key = data.org_unit.user_key

    location = await get_org_unit_location(mo, notification.org_unit_uuid)

    #####

    msg = EmailMessage()
    msg["Subject"] = "En medarbejder fjernes fra lederfanen"
    msg["From"] = settings.email_settings.sender

    if settings.alert_manager_removal_use_org_unit_emails:
        msg["To"] = await mo.get_institution_address(
            mo, notification.org_unit_uuid, one(org_unit.root).uuid
        )
    else:
        msg["To"] = set(settings.email_settings.receivers)
    # CC + BCC

    msg.set_content(
        f"Denne besked er for at gøre opmærksom på, at følgende medarbejder er blevet fjernet fra lederfanen i OS2mo:\n\n"
        f"Navn: {name}\n"
        f"Fratrædelsesdato: {notification.end_date}\n"
        f"Placering: {location}\n"
        f"Placering: {org_unit_user_key}\n"
        "På forhånd tak.\n"
        "Med venlig hilsen,\n"
        "OS2mo\n\n"
        "Denne besked kan ikke besvares."
    )
    return msg


# async def build_org_unit_email(notification: OrgUnitNotification, mo: GraphQLClient, settings: depends.Settings) -> EmailMessage:
#     # Pseudo
#     data = mo.get_some_data(notification.org_unit_uuid)
#     #
#     msg = EmailMessage()
#     msg["Subject"] = f"Manglende relation i Lønorganisation"
#     msg["From"] = settings.email_settings.sender
#
#     if settings.alert_manager_removal_use_org_unit_emails:
#         msg["To"] = await mo.get_institution_address(
#             mo, notification.org_unit_uuid, data.org_unit.root.uuid
#         )
#     else:
#         msg["To"] = set(settings.email_settings.receivers)
#
#     # CC + BCC
#
#     msg.set_content(
#         f"Denne besked er sendt som en påmindelse om at enheden: {data.org_unit.name} ikke er relateret til en enhed i Administrationsorganisationen."
#         "På forhånd tak.\n"
#         "Med venlig hilsen,\n"
#         "OS2mo\n\n"
#         "Denne besked kan ikke besvares."
#     )
#     return msg
