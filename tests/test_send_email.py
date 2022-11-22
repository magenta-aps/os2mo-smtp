import mo_smtp.send_email as send_email
import unittest


class EmailTest(unittest.TestCase):
    super().setUp()

    def test_empty_address(self) -> None:
        """
        For an empty receiver or sender address, should return ValueError
        """
        with self.assertRaises(ValueError):
            send_email.send_email(receiver="")
        with self.assertRaises(ValueError):
            send_email.send_email(sender="")

    def test_send_message(self) -> None:
        """
        Test that sent email reflects input accurately
        """
        message_args = {
            "receiver": ["jens@jens.jens", "mads@mads.mads"],
            "sender": "sine@sine.sine",
            "cc": ["anders@and.rap", "fedt@mule.hydr"],
            "bcc": ["rip@rap.rup", "snip@snap.snude"],
            "subject": "En meget vigtig besked",
            "body": "Brødteksten på den meget vigtige besked",
            "run_test": True,
        }

        # Retrieve MIMEText object from send_email
        message = send_email.send_email(**message_args)

        # Assert correct field mapping
        self.assertEqual(message["To"], message_args["receiver"])
        self.assertEqual(message["From"], message_args["sender"])
        self.assertEqual(message["CC"], message_args["cc"])
        self.assertEqual(message["BCC"], message_args["bcc"])
        self.assertEqual(message["Subject"], message_args["subject"])
