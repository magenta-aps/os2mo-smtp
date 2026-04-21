"""Integration tests for EmailClient using the real mailcatcher SMTP server."""

import httpx
import pytest
from fastramqpi.context import Context

from mo_smtp.config import EmailSettings, SMTPSecurity
from mo_smtp.mail import EmailClient

pytestmark = pytest.mark.integration_test

MAILCATCHER_API = "http://mailcatcher:1080"


@pytest.fixture
def email_client(monkeypatch, load_settings_overrides) -> EmailClient:
    monkeypatch.setenv("DRY_RUN", "False")
    settings = EmailSettings()
    context = Context({"user_context": {"email_settings": settings}})
    return EmailClient(context)


@pytest.fixture(autouse=True)
def clear_mailcatcher(respx_mock):
    """Allow HTTP to mailcatcher and clear messages before/after each test."""
    respx_mock.route(host="mailcatcher").pass_through()
    httpx.delete(f"{MAILCATCHER_API}/messages")
    yield
    httpx.delete(f"{MAILCATCHER_API}/messages")


def _get_messages() -> list[dict]:
    return httpx.get(f"{MAILCATCHER_API}/messages").json()


def _get_message_body(message_id: int) -> str:
    return httpx.get(f"{MAILCATCHER_API}/messages/{message_id}.plain").text


def test_send_email_delivers_to_mailcatcher(email_client: EmailClient):
    """Verify a real email is delivered through SMTP to mailcatcher."""
    email_client.send_email(
        receiver={"receiver@test.net"},
        subject="Test subject",
        body="Test body with æ, ø, and å",
        texttype="plain",
    )

    messages = _get_messages()
    assert len(messages) == 1

    msg = messages[0]
    assert msg["subject"] == "Test subject"
    assert email_client.sender in msg["sender"]
    assert "<receiver@test.net>" in msg["recipients"]

    body = _get_message_body(msg["id"])
    assert "Test body with æ, ø, and å" in body


def test_send_email_with_cc(email_client: EmailClient):
    """CC recipients receive the email."""
    email_client.send_email(
        receiver={"receiver@test.net"},
        cc={"cc@test.net"},
        subject="CC test",
        body="Body",
        texttype="plain",
    )

    messages = _get_messages()
    assert len(messages) == 1
    recipients = messages[0]["recipients"]
    assert "<receiver@test.net>" in recipients
    assert "<cc@test.net>" in recipients


def test_send_email_with_bcc(email_client: EmailClient):
    """BCC recipients receive the email but aren't in headers."""
    email_client.send_email(
        receiver={"receiver@test.net"},
        bcc={"bcc@test.net"},
        subject="BCC test",
        body="Body",
        texttype="plain",
    )

    messages = _get_messages()
    assert len(messages) == 1
    recipients = messages[0]["recipients"]
    assert "<receiver@test.net>" in recipients
    assert "<bcc@test.net>" in recipients


def test_dry_run_does_not_send(email_client: EmailClient):
    """When dry_run is True, no email is actually sent."""
    email_client.dry_run = True

    email_client.send_email(
        receiver={"receiver@test.net"},
        subject="Should not arrive",
        body="Body",
        texttype="plain",
    )

    messages = _get_messages()
    assert len(messages) == 0


def test_receiver_override(email_client: EmailClient):
    """When receiver_override is set, email goes to the override address only."""
    email_client.receiver_override = "override@test.net"

    email_client.send_email(
        receiver={"original@test.net"},
        cc={"cc@test.net"},
        subject="Override test",
        body="Body",
        texttype="plain",
    )

    messages = _get_messages()
    assert len(messages) == 1
    recipients = messages[0]["recipients"]
    assert "<override@test.net>" in recipients
    assert "<original@test.net>" not in recipients
    assert "<cc@test.net>" not in recipients


def test_starttls_not_implemented(email_client: EmailClient):
    """STARTTLS raises NotImplementedError."""
    email_client.smtp_security = SMTPSecurity.STARTTLS
    with pytest.raises(
        NotImplementedError, match="STARTTLS support has not been implemented"
    ):
        email_client.send_email(
            receiver={"a@test.com"},
            subject="Subject",
            body="Body",
        )
