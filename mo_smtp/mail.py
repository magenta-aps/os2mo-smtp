# Sends an email
from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL
from .config import SMTPSecurity

import structlog

logger = structlog.get_logger()


class EmailClient:
    def __init__(self, email_settings):
        self.smtp_user = email_settings.smtp_user
        self.smtp_password = email_settings.smtp_password
        self.smtp_host = email_settings.smtp_host
        self.smtp_port = email_settings.smtp_port
        self.smtp_security = email_settings.smtp_security
        self.sender = email_settings.sender
        self.dry_run = email_settings.dry_run
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
            recipients = [self.receiver_override]
        else:
            msg["To"] = ", ".join(receiver)
            msg["CC"] = ", ".join(cc)
            recipients = list(receiver) + list(cc)

        bcc_list = list(bcc)

        # Print message content to log
        for key in msg.keys():
            logger.info(f"{key}: {msg[key]}")
        # 1st decode seems to decode from email-encoding to binary string
        # 2nd decode decodes from binary string to human-readable
        # (including special chars)
        payload = msg.get_payload(decode=True)
        logger.info(
            "Body: "
            + (payload.decode() if isinstance(payload, bytes) else str(payload))
        )

        if self.smtp_security is SMTPSecurity.STARTTLS:
            raise NotImplementedError(
                "STARTTLS support has not been implemented. Consider using implicit TLS, which is generally considered more secure."
            )
        smtp_cls = SMTP_SSL if self.smtp_security is SMTPSecurity.TLS else SMTP
        smtp = smtp_cls(host=self.smtp_host, port=self.smtp_port)
        if self.smtp_user and self.smtp_password:
            smtp.login(user=self.smtp_user, password=self.smtp_password)

        if not self.dry_run:
            smtp.send_message(msg, to_addrs=recipients + bcc_list)
            smtp.quit()
            logger.info("Email has been sent")
        else:
            logger.info("This was a dry run")
        return msg
