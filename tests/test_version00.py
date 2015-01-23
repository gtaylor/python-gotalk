from unittest import TestCase

from gotalk.protocol.messages import read_version_message


class VersionTest(TestCase):

    def test_read_valid(self):
        valid = "00"
        self.assertEqual(read_version_message(valid), valid)
