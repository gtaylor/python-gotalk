from unittest import TestCase

from gotalk.protocol.messages import read_version_message, write_message, \
    read_message
from gotalk.protocol.version00.messages import ProtocolVersionMessage, \
    SingleRequestMessage


_PROTO_VERSION = "00"


class VersionTest(TestCase):

    def test_read_valid(self):
        """
        Test parsing of valid version message.
        """

        valid = _PROTO_VERSION
        self.assertEqual(read_version_message(valid), valid)

    def test_write_version(self):
        """
        Test the writing of a version message.
        """

        message = ProtocolVersionMessage()
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, _PROTO_VERSION)


class SingleRequestMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of some properly formed messages.
        """

        valid1 = 'r001004echo00000019{"message":"Hello World"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertEqual(message.request_id, "001")
        self.assertEqual(message.operation, "echo")
        self.assertEqual(message.payload, '{"message":"Hello World"}')

    def test_write(self):
        """
        Tests writing various writes to make sure our serializtion is good.
        """

        message = SingleRequestMessage(
            request_id="001", operation="echo", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'r001004echo0000000bHello World')
