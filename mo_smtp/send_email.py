# Sends an email
from email.mime.text import MIMEText
import asyncio
from aiosmtplib import SMTP


async def send_email(
    receiver: [str] = {"receive@example.net"},
    sender: str = "send@example.net",
    subject: str = "Subject line",
    body: str = "This is a test message",
    textType: str = "plain",
    hostname: str = "172.17.0.1",
    port: int = 2525,
    cc: [str] = [],
    bcc: [str] = [],
) -> None:
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
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["CC"] = ", ".join(cc)
    msg["To"] = ", ".join(receiver)

    async with SMTP(hostname, port) as smtp:
        await smtp.send_message(msg)

    return
