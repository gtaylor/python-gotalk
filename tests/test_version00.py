from unittest import TestCase

from gotalk.protocol.messages import read_version_message, write_message, \
    read_message
from gotalk.protocol.version00.messages import ProtocolVersionMessage, \
    SingleRequestMessage, SingleResultMessage, StreamRequestMessage, \
    StreamRequestPartMessage, StreamResultMessage, ErrorResultMessage, \
    NotificationMessage


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
        Tests the reading of properly formed single request messages.
        """

        valid1 = 'r001004echo00000019{"message":"Hello World"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, SingleRequestMessage)
        self.assertEqual(message.request_id, "001")
        self.assertEqual(message.operation, "echo")
        self.assertEqual(message.payload, '{"message":"Hello World"}')

    def test_write(self):
        """
        Makes sure our single request serialization is good.
        """

        message = SingleRequestMessage(
            request_id="001", operation="echo", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'r001004echo0000000bHello World')


class SingleResultMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed single result messages.
        """

        valid1 = 'R00100000019{"message":"Hello World"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, SingleResultMessage)
        self.assertEqual(message.request_id, "001")
        self.assertEqual(message.payload, '{"message":"Hello World"}')

    def test_write(self):
        """
        Makes sure our single result serialization is good.
        """

        message = SingleResultMessage(
            request_id="001", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'R0010000000bHello World')


class StreamRequestMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed stream request messages.
        """

        valid1 = 's001004echo0000000b{"message":'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, StreamRequestMessage)
        self.assertEqual(message.request_id, "001")
        self.assertEqual(message.operation, "echo")
        self.assertEqual(message.payload, '{"message":')

    def test_write(self):
        """
        Makes sure our stream request serialization is good.
        """

        message = StreamRequestMessage(
            request_id="001", operation="echo", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 's001004echo0000000bHello World')


class StreamRequestPartMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed stream request part messages.
        """

        valid1 = 'p0010000000e"Hello World"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, StreamRequestPartMessage)
        self.assertEqual(message.request_id, "001")
        self.assertEqual(message.payload, '"Hello World"}')

    def test_write(self):
        """
        Makes sure our stream request serialization is good.
        """

        message = StreamRequestPartMessage(
            request_id="001", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'p0010000000bHello World')


class StreamResultMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed stream result messages.
        """

        valid1 = 'S0010000000b{"message":'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, StreamResultMessage)
        self.assertEqual(message.request_id, "001")
        self.assertEqual(message.payload, '{"message":')

    def test_write(self):
        """
        Makes sure our stream result serialization is good.
        """

        message = StreamResultMessage(
            request_id="001", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'S0010000000bHello World')


class ErrorResultMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed error result messages.
        """

        valid1 = 'E00100000026{"error":"Unknown operation \"echo\""}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, ErrorResultMessage)
        self.assertEqual(message.request_id, "001")
        self.assertEqual(message.payload, '{"error":"Unknown operation \"echo\""}')

    def test_write(self):
        """
        Makes sure our error result serialization is good.
        """

        message = ErrorResultMessage(
            request_id="001", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'E0010000000bHello World')


class NotificationMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed notification messages.
        """

        valid1 = 'n00cchat message00000032{"message":"Hi","from":"nthn","chat_room":"gonuts"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, NotificationMessage)
        self.assertEqual(message.n_type, "chat message")
        self.assertEqual(message.payload, '{"message":"Hi","from":"nthn","chat_room":"gonuts"}')

    def test_write(self):
        """
        Makes sure our notification serialization is good.
        """

        message = NotificationMessage(
            n_type="test_type", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'n009test_type0000000bHello World')
