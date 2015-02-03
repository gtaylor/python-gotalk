from unittest import TestCase
from gotalk.exceptions import PayloadTooLongError, OperationTooLongError

from gotalk.protocol.messages import read_version_message, write_message, \
    read_message
from gotalk.protocol.version01.messages import ProtocolVersionMessage, \
    SingleRequestMessage, SingleResultMessage, StreamRequestMessage, \
    StreamRequestPartMessage, StreamResultMessage, ErrorResultMessage, \
    NotificationMessage


_PROTO_VERSION = "01"


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


class CommonTest(TestCase):
    """
    The tests in this case apply to almost every message type.
    """

    def test_large_payload(self):
        """
        Make sure payload length errors are triggering.
        """

        self.skipTest("See if there's a way to do this without the RAM usage.")
        valid_payload = "#" * SingleRequestMessage.payload_max_length
        message = SingleRequestMessage(
            request_id="0001", operation="echo", payload=valid_payload)
        # This shouldn't raise an error.
        write_message(message)
        # Now make it too big.
        message.payload += "#"
        self.assertRaises(PayloadTooLongError, write_message, message)

    def test_large_operation(self):
        """
        Make sure operation length errors are triggering.
        """

        valid_operation = "#" * SingleRequestMessage.operation_max_length
        message = SingleRequestMessage(
            request_id="0001", operation=valid_operation, payload="yay")
        # This shouldn't raise an error.
        write_message(message)
        # Now make it too big (by one).
        message.operation += "#"
        self.assertRaises(OperationTooLongError, write_message, message)


class SingleRequestMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed single request messages.
        """

        valid1 = 'r0001004echo00000019{"message":"Hello World"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, SingleRequestMessage)
        self.assertEqual(message.request_id, "0001")
        self.assertEqual(message.operation, "echo")
        self.assertEqual(message.payload, '{"message":"Hello World"}')

    def test_write(self):
        """
        Makes sure our single request serialization is good.
        """

        message = SingleRequestMessage(
            request_id="0001", operation="echo", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'r0001004echo0000000bHello World')


class SingleResultMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed single result messages.
        """

        valid1 = 'R000100000019{"message":"Hello World"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, SingleResultMessage)
        self.assertEqual(message.request_id, "0001")
        self.assertEqual(message.payload, '{"message":"Hello World"}')

    def test_write(self):
        """
        Makes sure our single result serialization is good.
        """

        message = SingleResultMessage(
            request_id="0001", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'R00010000000bHello World')


class StreamRequestMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed stream request messages.
        """

        valid1 = 's0001004echo0000000b{"message":'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, StreamRequestMessage)
        self.assertEqual(message.request_id, "0001")
        self.assertEqual(message.operation, "echo")
        self.assertEqual(message.payload, '{"message":')

    def test_write(self):
        """
        Makes sure our stream request serialization is good.
        """

        message = StreamRequestMessage(
            request_id="0001", operation="echo", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 's0001004echo0000000bHello World')


class StreamRequestPartMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed stream request part messages.
        """

        valid1 = 'p00010000000e"Hello World"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, StreamRequestPartMessage)
        self.assertEqual(message.request_id, "0001")
        self.assertEqual(message.payload, '"Hello World"}')

    def test_write(self):
        """
        Makes sure our stream request serialization is good.
        """

        message = StreamRequestPartMessage(
            request_id="0001", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'p00010000000bHello World')


class StreamResultMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed stream result messages.
        """

        valid1 = 'S00010000000b{"message":'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, StreamResultMessage)
        self.assertEqual(message.request_id, "0001")
        self.assertEqual(message.payload, '{"message":')

    def test_write(self):
        """
        Makes sure our stream result serialization is good.
        """

        message = StreamResultMessage(
            request_id="0001", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'S00010000000bHello World')


class ErrorResultMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed error result messages.
        """

        valid1 = 'E000100000026{"error":"Unknown operation \"echo\""}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, ErrorResultMessage)
        self.assertEqual(message.request_id, "0001")
        self.assertEqual(message.payload, '{"error":"Unknown operation \"echo\""}')

    def test_write(self):
        """
        Makes sure our error result serialization is good.
        """

        message = ErrorResultMessage(
            request_id="0001", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'E00010000000bHello World')


class NotificationMessageTest(TestCase):

    def test_valid_read(self):
        """
        Tests the reading of properly formed notification messages.
        """

        valid1 = 'n00cchat message00000032{"message":"Hi","from":"nthn","chat_room":"gonuts"}'
        message = read_message(valid1, _PROTO_VERSION)
        self.assertIsInstance(message, NotificationMessage)
        self.assertEqual(message.name, "chat message")
        self.assertEqual(message.payload, '{"message":"Hi","from":"nthn","chat_room":"gonuts"}')

    def test_write(self):
        """
        Makes sure our notification serialization is good.
        """

        message = NotificationMessage(name="test_name", payload="Hello World")
        m_bytes = write_message(message)
        self.assertEqual(m_bytes, 'n009test_name0000000bHello World')
