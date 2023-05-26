from email.mime.text import MIMEText
from smtpd import SMTPServer
from smtplib import SMTPNotSupportedError
from unittest.mock import MagicMock
from unittest.mock import patch

import mo_smtp.send_email as send_email


async def test_send_message_testing_false() -> None:
    """
    Test that sent email reflects input accurately
    """

    receiver = {"receiver1@test.net", "receiver2@test.net"}
    sender = "sender@test.net"
    smtp_host = "localhost"
    smtp_port = 2500
    cc = {"cc1@test.net", "cc2@test.net"}
    bcc = {"bcc1@test.net", "bcc2@test.net"}
    subject = "A very important message"
    body = "The body of the very important message with a, ø, and å"
    texttype = "plain"
    testing = False

    smtpmock = MagicMock()
    smtpmock.ehlo_or_helo_if_needed.return_value = None
    smtpmock.starttls.return_value = None
    smtpmock.quit.return_value = None

    # Retrieve MIMEText object from send_email
    with patch("mo_smtp.send_email.SMTP.send_message", return_value=None), patch(
        "mo_smtp.send_email.SMTP", return_value=smtpmock
    ):
        SMTPServer((smtp_host, smtp_port), (smtp_host, smtp_port))
        message = send_email.send_email(
            receiver=receiver,
            sender=sender,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            texttype=texttype,
            testing=testing,
        )

        expected_message = MIMEText(body, texttype, _charset="utf-8")
        expected_message["Subject"] = subject
        expected_message["From"] = sender
        expected_message["To"] = ", ".join(receiver)
        expected_message["CC"] = ", ".join(cc)
        expected_message["BCC"] = ", ".join(bcc)

        # Assert correct return type
        assert type(message) == MIMEText

        # Assert correct field mapping
        for key in message.keys():
            assert message[key] == expected_message[key]


async def test_send_message_testing_true() -> None:
    """
    Test that sent email reflects input accurately
    """

    receiver = {"receiver1@test.net", "receiver2@test.net"}
    sender = "sender@test.net"
    smtp_host = "localhost"
    smtp_port = 2500
    cc = {"cc1@test.net", "cc2@test.net"}
    bcc = {"bcc1@test.net", "bcc2@test.net"}
    subject = "A very important message"
    body = "The body of the very important message"
    texttype = "plain"
    testing = True

    smtpmock = MagicMock()
    smtpmock.ehlo_or_helo_if_needed.return_value = None
    smtpmock.starttls.return_value = None
    smtpmock.quit.return_value = None

    # Retrieve MIMEText object from send_email
    with patch("mo_smtp.send_email.SMTP.send_message", return_value=None), patch(
        "mo_smtp.send_email.SMTP", return_value=smtpmock
    ):
        message = send_email.send_email(
            receiver=receiver,
            sender=sender,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            texttype=texttype,
            testing=testing,
        )

        expected_message = MIMEText(body, texttype, _charset="utf-8")
        expected_message["Subject"] = subject
        expected_message["From"] = sender
        expected_message["To"] = ", ".join(receiver)
        expected_message["CC"] = ", ".join(cc)
        expected_message["BCC"] = ", ".join(bcc)

        # Assert correct return type
        assert type(message) == MIMEText

        # Assert correct field mapping
        for key in message.keys():
            assert message[key] == expected_message[key]


async def test_send_message_tls_error() -> None:
    """
    Test that sent email reflects input accurately
    """

    receiver = {"receiver1@test.net", "receiver2@test.net"}
    sender = "sender@test.net"
    smtp_host = "localhost"
    smtp_port = 2525
    cc = {"cc1@test.net", "cc2@test.net"}
    bcc = {"bcc1@test.net", "bcc2@test.net"}
    subject = "A very important message"
    body = "The body of the very important message with a, ø, and å"
    texttype = "plain"
    testing = False

    smtpmock = MagicMock()
    smtpmock.ehlo_or_helo_if_needed.return_value = None
    smtpmock.starttls.side_effect = SMTPNotSupportedError(
        "TLS not supported by SMTP server"
    )
    smtpmock.starttls.return_value = None
    smtpmock.quit.return_value = None

    # Retrieve MIMEText object from send_email
    with patch("mo_smtp.send_email.SMTP.send_message", return_value=None), patch(
        "mo_smtp.send_email.SMTP", return_value=smtpmock
    ):
        SMTPServer((smtp_host, smtp_port), (smtp_host, smtp_port))
        message = send_email.send_email(
            receiver=receiver,
            sender=sender,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            texttype=texttype,
            testing=testing,
        )

        expected_message = MIMEText(body, texttype, _charset="utf-8")
        expected_message["Subject"] = subject
        expected_message["From"] = sender
        expected_message["To"] = ", ".join(receiver)
        expected_message["CC"] = ", ".join(cc)
        expected_message["BCC"] = ", ".join(bcc)

        # Assert correct return type
        assert type(message) == MIMEText

        # Assert correct field mapping
        for key in message.keys():
            assert message[key] == expected_message[key]
