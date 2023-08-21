# Sends an email
from email.mime.text import MIMEText
from smtplib import SMTP
from smtplib import SMTPNotSupportedError

import structlog
from fastramqpi.context import Context

logger = structlog.get_logger()


class EmailClient:
    def __init__(self, context: Context):
        email_settings = context["user_context"]["email_settings"]
        self.smtp = SMTP(host=email_settings.smtp_host, port=email_settings.smtp_port)
        self.sender = email_settings.sender
        self.testing = email_settings.testing
        self.receiver_override = email_settings.receiver_override

    def send_email(
        self,
        receiver: set[str],
        subject: str,
        body: str,
        texttype: str = "plain",
        cc: set[str] = {""},
        bcc: set[str] = {""},
        allow_receiver_override=True,
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
            allow_receiver_override : Whether we should override the receiver with
                the address specified in settings.receiver_override
                Example: True
        """

        msg = MIMEText(body, texttype, _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = self.sender
        if self.receiver_override and allow_receiver_override:
            msg["To"] = self.receiver_override
        else:
            msg["To"] = ", ".join(receiver)
            msg["CC"] = ", ".join(cc) or None
            msg["BCC"] = ", ".join(bcc) or None

        # Print message content to log
        for key in msg.keys():
            logger.info(f"{key}: {msg[key]}")
        # 1st decode seems to decode from email-encoding to binary string
        # 2nd decode decodes from binary string to human-readable
        # (including special chars)
        logger.info("Body: " + msg.get_payload(decode=True).decode())

        if not self.testing:
            try:
                self.smtp.starttls()
                self.smtp.ehlo_or_helo_if_needed()
            except SMTPNotSupportedError:
                logger.info("SMTP server doesn't use TLS. TLS ignored")
            self.smtp.send_message(msg)  # type: ignore
        else:
            logger.info("This was a test run. No message was sent")
        return msg
