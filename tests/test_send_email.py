import mo_smtp.send_email as send_email
import unittest


class EmailTest(unittest.TestCase):
    def test_empty_address(self) -> None:
        """
        For an empty receiver or sender address, should return ValueError
        """
        with self.assertRaises(ValueError):
            send_email.send_email(receiver="")
            send_email.send_email(sender="")
