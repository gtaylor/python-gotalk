"""
The top-level API for Gotalk message marshalling/unmarshalling.
"""

from gotalk.exceptions import InvalidProtocolVersionError, \
    InvalidMessageTypeIDError
from gotalk.protocol import version00
from gotalk.protocol.defines import MESSAGE_TYPE_TO_CLASS_MAP

PROTOCOL_VERSION_MAP = {
    0: version00,
}


def read_version_message(m_bytes):
    """
    Communication alway starts with an exchange of the protocol version.
    Hopefully this won't ever change...

    :param str m_bytes: The byte string to parse.
    :rtype: int
    :returns: The version number shared in the message.
    :raises: InvalidProtocolVersionError if an invalid version is encountered.
    """

    try:
        # TODO: Should we enforce the 2-byte size here, or this OK?
        version_str = int(m_bytes[0:2])
    except ValueError:
        raise InvalidProtocolVersionError()
    return version_str


def parse_message(m_bytes, proto_version):
    """
    Parses a messages, spitting out a properly formed instance of the
    appropriate ``GotalkMessage`` sub-class.

    :param str m_bytes: The unmodified m_bytes to parse.
    :param int proto_version: The protocol version to use in the exchange.
    :rtype: GotalkMessage
    :returns: One of the ``GotalkMessage` sub-classe.
    """

    version = int(proto_version)
    # This is the sub-module for the specified proto version.
    proto_module = PROTOCOL_VERSION_MAP[version]

    type_id = m_bytes[0]
    try:
        msg_class_name = MESSAGE_TYPE_TO_CLASS_MAP[type_id]
    except KeyError:
        raise InvalidMessageTypeIDError()
    msg_class = getattr(proto_module, msg_class_name)
    return msg_class.from_bytes(m_bytes)
