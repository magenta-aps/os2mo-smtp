from email.mime.text import MIMEText

import pytest
from email_validator import EmailNotValidError

import mo_smtp.send_email as send_email

# TODO: Install email-validator, to typecheck strings that should be email addresses


async def test_empty_address() -> None:
    """
    For an empty receiver or sender address, should return ValueError
    """
    with pytest.raises(EmailNotValidError):
        await send_email.send_email(receiver={""}, testing=True)
    with pytest.raises(TypeError):
        await send_email.send_email(receiver=None, testing=True)  # type: ignore
    with pytest.raises(ValueError):
        await send_email.send_email(sender="", testing=True)
    # with pytest.raises(TypeError):
    # await send_email.send_email(sender=None)


async def test_send_message() -> None:
    """
    Test that sent email reflects input accurately
    """

    receiver = {"jens@jens.jens", "mads@mads.mads"}
    sender = "sine@sine.sine"
    cc = {"anders@and.rap", "fedt@mule.hydr"}
    bcc = {"rip@rap.rup", "snip@snap.snude"}
    subject = "En meget vigtig besked"
    body = "Brødteksten på den meget vigtige besked"
    texttype = "plain"
    testing = True

    # Retrieve MIMEText object from send_email
    message = await send_email.send_email(
        receiver=receiver,
        sender=sender,
        cc=cc,
        bcc=bcc,
        subject=subject,
        body=body,
        texttype=texttype,
        testing=testing,
    )

    expected_message = MIMEText(body, texttype)
    expected_message["Subject"] = subject
    expected_message["From"] = sender
    expected_message["To"] = ", ".join(receiver)
    expected_message["CC"] = ", ".join(cc)
    expected_message["BCC"] = ", ".join(bcc)
    expected_message

    # Assert correct return type
    assert type(message) == MIMEText

    # Assert correct field mapping
    for key in message.keys():
        assert message[key] == expected_message[key]
