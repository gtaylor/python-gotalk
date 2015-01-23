"""
The top-level API for Gotalk message marshalling/unmarshalling.
"""

from gotalk.exceptions import InvalidMessageTypeIDError, \
    InvalidProtocolVersionError
from gotalk.protocol import version00
from gotalk.protocol.defines import MESSAGE_TYPE_TO_CLASS_MAP

PROTOCOL_VERSION_MAP = {
    "00": version00,
}


def read_version_message(m_bytes):
    """
    Communication alway starts with an exchange of the protocol version.
    Hopefully this won't ever change...

    :param str m_bytes: The byte string to parse.
    :rtype: int
    :returns: The version number shared in the message.
    :raises: InvalidProtocolVersionError if the version is mal-formed.
    """

    if len(m_bytes) != 2:
        raise InvalidProtocolVersionError()
    version_str = m_bytes[0:2]
    return version_str


def read_message(m_bytes, proto_version):
    """
    Parses a messages, spitting out a properly formed instance of the
    appropriate ``GotalkMessage`` sub-class.

    :param str m_bytes: The unmodified m_bytes to parse.
    :param str proto_version: The protocol version to use in the exchange.
    :rtype: GotalkMessage
    :returns: One of the ``GotalkMessage` sub-class.
    :raises: InvalidProtocolVersionError if we don't know how to handle
        the encountered version.
    """

    # This is the sub-module for the specified proto version.
    try:
        proto_module = PROTOCOL_VERSION_MAP[proto_version]
    except KeyError:
        # TODO: Depending on the backwards-compatibility policy with gotalk,
        # we might be able to fall back to the latest known version and
        # potentially limp along. Too early to know.
        raise InvalidProtocolVersionError("Invalid gotalk protocol version.")

    type_id = m_bytes[0]
    try:
        msg_class_name = MESSAGE_TYPE_TO_CLASS_MAP[type_id]
    except KeyError:
        raise InvalidMessageTypeIDError()
    msg_class = getattr(proto_module, msg_class_name)
    return msg_class.from_bytes(m_bytes)


def write_message(message):
    """
    Given a message, dump it to bytes.

    :param message: An instance of a GotalkMessage child.
    :rtype: str
    :returns: The bytes to send for the given message.
    """

    return message.to_bytes()
