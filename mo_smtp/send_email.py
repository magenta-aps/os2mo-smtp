# Sends an email
from email.mime.text import MIMEText
import asyncio
from aiosmtplib import SMTP


async def send_email(
    receiver: set[str] = {"receive@example.net"},
    sender: str = "send@example.net",
    subject: str = "Subject line",
    body: str = "This is a test message",
    texttype: str = "plain",
    hostname: str = "172.17.0.1",
    port: int = 2525,
    cc: list[str, None] = [],
    bcc: list[str, None] = [],
    run_test: bool = False,
) -> None|type(MIMEText):
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
    print(msg)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["CC"] = ", ".join(cc)
    msg["BCC"] = ", ".join(bcc)
    msg["To"] = ", ".join(receiver)

    #print(msg)
    #print(dir(msg))
    #print(msg.values())
    #print(msg.get_payload(decode=True))
    # print(msg.as_string())
    # print(msg.items())
    # for item in msg.raw_items():
    #    print(item)
    # print(msg.raw_items())
    # print(msg.get_content_maintype())
    # for item in msg.walk():
    #    print(item)
    # print(msg.walk())
    if run_test:
        return msg

    async with SMTP(hostname, port) as smtp:
        await smtp.send_message(msg)

    return
