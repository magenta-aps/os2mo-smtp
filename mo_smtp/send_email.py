# Sends an email
from email.mime.text import MIMEText

from aiosmtplib import SMTP

"""
from typing import runtime_checkable
@runtime_checkable
class SMTP_obj(SMTP):
    async def send_message(msg):
        super().send_message(msg)
"""

"""
Use:
Servarname: localhost
ServerAdmin: sysadmins@magenta.dk

"""


async def send_email(
    receiver: set[str] = {"receive@example.net"},
    sender: str = "send@example.net",
    subject: str = "Subject line",
    body: str = "This is a test message",
    texttype: str = "plain",
    hostname: str = "172.17.0.1",
    port: int = 2525,
    cc: set[str] = {""},
    bcc: set[str] = {""},
) -> MIMEText:
    """
    Sends outgoing email given parameters

    Args:
        receiver: List of receiver email addresses
        sender: Sender email address
        subject: Message subject
        body: Message body
        textType: Mime subtype of text. Can also be 'html'
        hostname: SMTP host IP address
        port: SMTP server connection port
        cc: List of CC'ed email addresses
        bcc: List of BCC'ed email addresses
    """
    msg = MIMEText(body, texttype)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["CC"] = ", ".join(iter(cc))
    msg["BCC"] = ", ".join(iter(bcc))
    msg["To"] = ", ".join(receiver)

    async with SMTP(hostname, port) as smtp:
        await smtp.send_message(msg)  # type: ignore
    return msg
