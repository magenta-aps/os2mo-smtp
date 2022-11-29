import unittest
from email.mime.text import MIMEText

import mo_smtp.send_email as send_email


class EmailTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

    async def test_empty_address(self) -> None:
        """
        For an empty receiver or sender address, should return ValueError
        """
        with self.assertRaises(ValueError):
            await send_email.send_email(receiver={""})
        with self.assertRaises(ValueError):
            await send_email.send_email(sender="")

    async def test_send_message(self) -> None:
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

        # Retrieve MIMEText object from send_email
        message = await send_email.send_email(
            receiver=receiver,
            sender=sender,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            texttype=texttype,
        )

        expected_message = MIMEText(body, texttype)
        expected_message["Subject"] = subject
        expected_message["From"] = sender
        expected_message["To"] = ", ".join(receiver)
        expected_message["CC"] = ", ".join(cc)
        expected_message["BCC"] = ", ".join(bcc)

        # Assert correct return type
        self.assertIsInstance(message, MIMEText)

        # Assert correct field mapping
        self.assertEqual(message, expected_message)


unittest.main()
