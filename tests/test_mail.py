from email.mime.text import MIMEText
from smtplib import SMTPNotSupportedError
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from fastramqpi.context import Context

from mo_smtp.mail import EmailClient


@pytest.fixture
def email_settings() -> MagicMock:
    email_settings = MagicMock()
    email_settings.smtp_host = "0.0.0.0"
    email_settings.smtp_port = 1025
    email_settings.sender = "sender@test.net"
    email_settings.testing = False
    email_settings.receiver_override = ""
    return email_settings


@pytest.fixture
async def email_client(email_settings: MagicMock) -> EmailClient:
    context = Context({"user_context": {"email_settings": email_settings}})

    with patch("mo_smtp.mail.SMTP", return_value=MagicMock()):
        return EmailClient(context)


async def test_send_message_testing_false(email_client: EmailClient) -> None:
    """
    Test that sent email reflects input accurately
    """

    receiver = {"receiver1@test.net", "receiver2@test.net"}
    cc = {"cc1@test.net", "cc2@test.net"}
    bcc = {"bcc1@test.net", "bcc2@test.net"}
    subject = "A very important message"
    body = "The body of the very important message with a, ø, and å"
    texttype = "plain"

    # Retrieve MIMEText object from send_email

    smtpmock = MagicMock()
    with patch("mo_smtp.mail.SMTP", return_value=smtpmock):
        message = email_client.send_email(
            receiver=receiver,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            texttype=texttype,
        )

        expected_message = MIMEText(body, texttype, _charset="utf-8")
        expected_message["Subject"] = subject
        expected_message["From"] = "sender@test.net"
        expected_message["To"] = ", ".join(receiver)
        expected_message["CC"] = ", ".join(cc)
        expected_message["BCC"] = ", ".join(bcc)

        # Assert correct return type
        assert type(message) is MIMEText

        # Assert correct field mapping
        for key in message.keys():
            assert message[key] == expected_message[key]

        smtpmock.send_message.assert_called_once()  # type: ignore


async def test_send_message_testing_true(email_client: EmailClient) -> None:
    """
    Test that sent email reflects input accurately
    """

    receiver = {"receiver1@test.net", "receiver2@test.net"}
    cc = {"cc1@test.net", "cc2@test.net"}
    bcc = {"bcc1@test.net", "bcc2@test.net"}
    subject = "A very important message"
    body = "The body of the very important message"
    texttype = "plain"

    # Retrieve MIMEText object from send_email
    email_client.testing = True

    smtpmock = MagicMock()
    with patch("mo_smtp.mail.SMTP", return_value=smtpmock):
        message = email_client.send_email(
            receiver=receiver,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            texttype=texttype,
        )

        expected_message = MIMEText(body, texttype, _charset="utf-8")
        expected_message["Subject"] = subject
        expected_message["From"] = "sender@test.net"
        expected_message["To"] = ", ".join(receiver)
        expected_message["CC"] = ", ".join(cc)
        expected_message["BCC"] = ", ".join(bcc)

        # Assert correct return type
        assert type(message) is MIMEText

        # Assert correct field mapping
        for key in message.keys():
            assert message[key] == expected_message[key]

        smtpmock.send_message.assert_not_called()  # type: ignore


async def test_send_message_tls_error(email_client: EmailClient) -> None:
    """
    Test that sent email reflects input accurately
    """

    receiver = {"receiver1@test.net", "receiver2@test.net"}
    cc = {"cc1@test.net", "cc2@test.net"}
    bcc = {"bcc1@test.net", "bcc2@test.net"}
    subject = "A very important message"
    body = "The body of the very important message with a, ø, and å"
    texttype = "plain"

    smtpmock = MagicMock()
    smtpmock.starttls.side_effect = SMTPNotSupportedError(
        "TLS not supported by SMTP server"
    )

    with patch("mo_smtp.mail.SMTP", return_value=smtpmock):
        # Retrieve MIMEText object from send_email
        message = email_client.send_email(
            receiver=receiver,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            texttype=texttype,
        )

        expected_message = MIMEText(body, texttype, _charset="utf-8")
        expected_message["Subject"] = subject
        expected_message["From"] = "sender@test.net"
        expected_message["To"] = ", ".join(receiver)
        expected_message["CC"] = ", ".join(cc)
        expected_message["BCC"] = ", ".join(bcc)

        # Assert correct return type
        assert type(message) is MIMEText

        # Assert correct field mapping
        for key in message.keys():
            assert message[key] == expected_message[key]


async def test_send_message_receiver_override(email_client: EmailClient):
    receiver = {"receiver1@test.net", "receiver2@test.net"}
    cc = {"cc1@test.net", "cc2@test.net"}
    bcc = {"bcc1@test.net", "bcc2@test.net"}
    subject = "A very important message"
    body = "The body of the very important message with a, ø, and å"
    texttype = "plain"

    # Retrieve MIMEText object from send_email
    smtpmock = MagicMock()
    with patch("mo_smtp.mail.SMTP", return_value=smtpmock):
        email_client.receiver_override = "mail@test.com"
        message = email_client.send_email(
            receiver=receiver,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            texttype=texttype,
        )

        assert "CC" not in message
        assert "BCC" not in message
        assert message["To"] == "mail@test.com"
