# Sends an email
from email.mime.text import MIMEText
from smtplib import SMTP
from smtplib import SMTPNotSupportedError

import structlog

logger = structlog.get_logger()


class EmailClient:
    def __init__(self):
        pass

    def send_email(
        self,
        receiver: set[str],
        sender: str,
        subject: str,
        body: str,
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

        msg = MIMEText(body, texttype, _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["CC"] = ", ".join(cc)
        msg["BCC"] = ", ".join(bcc)
        msg["To"] = ", ".join(receiver)

        # Print message content to log
        for key in msg.keys():
            logger.info(f"{key}: {msg[key]}")
        # 1st decode seems to decode from email-encoding to binary string
        # 2nd decode decodes from binary string to human-readable
        # (including special chars)
        logger.info("Body: " + msg.get_payload(decode=True).decode())

        if not testing:
            smtp = SMTP(host=smtp_host, port=smtp_port)
            try:
                smtp.starttls()
                smtp.ehlo_or_helo_if_needed()
            except SMTPNotSupportedError:
                logger.info("SMTP server doesn't use TLS. TLS ignored")
            smtp.send_message(msg)  # type: ignore
            smtp.quit()
        return msg
