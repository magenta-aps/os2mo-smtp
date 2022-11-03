# Sends an email
from email.mime.text import MIMEText

import structlog
from aiosmtplib import SMTP

logger = structlog.get_logger()


async def send_email(
    receiver: set[str],
    sender: str,
    subject: str,
    body: str,
    # hostname and port send messages to nanoq's relay server
    smtp_host: str,
    smtp_port: int,
    texttype: str = "plain",
    cc: set[str] = {""},
    bcc: set[str] = {""},
    testing: bool = False,
) -> MIMEText:
    """
    Sends outgoing email given parameters

    Args:
        receiver: Set of receiver email addresses
            Example: {"receive@example.net"}
        sender: Sender email address
            Example: "sender@example.net"
        subject: Message subject
            Example: "Subject line"
        body: Message body
            Example: "This is a test message"
        textType: Mime subtype of text. Can also be 'html'
            Example: "plain"
        hostname: SMTP host IP address
            Example: "hostname.example.net" or "123.45.67.890"
        port: SMTP server connection port
            Example: 25
        cc: List of CC'ed email addresses
            Example: {"person@thing.net", "otherperson@something.com"}
        bcc: List of BCC'ed email addresses
            Example: {"person@thing.net", "otherperson@something.com"}
        testing: Whether the function is being run in a testing environment
            Example: True
    """

    msg = MIMEText(body, texttype, _charset="iso-8859-10")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["CC"] = ", ".join(cc)
    msg["BCC"] = ", ".join(bcc)
    msg["To"] = ", ".join(receiver)

    logger.info(msg)
    if not testing:
        await SMTP(smtp_host, smtp_port).send_message(msg)  # type: ignore
    return msg
