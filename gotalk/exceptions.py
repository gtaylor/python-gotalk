"""
General, non-protocol-version-specific exceptions.
"""


class InvalidProtocolVersionError(Exception):
    """
    Raised when encountering a protocol version that we don't understand, or
    in the presence of a malformed version exchange.
    """

    pass


class InvalidMessageTypeIDError(Exception):
    """
    Raised when an invalid message type ID prefix is encountered. This is
    usually due to a malformed message, or we're dealing with a different
    version of the protocol that we don't understand.
    """

    pass


class InvalidOperationError(Exception):
    """
    Raised when a operation is somehow invalid. Also serves as a base class for
    other, more specific operation errors.
    """

    pass


class OperationTooLongError(InvalidOperationError):
    """
    Raised when trying to send a message whose operation exceeds the
    operation limit.
    """

    pass


class InvalidPayloadError(Exception):
    """
    Raised when a payload is somehow invalid. Also serves as a base class for
    other, more specific payload errors.
    """

    pass


class PayloadTooLongError(InvalidPayloadError):
    """
    Raised when trying to send a message whose payload exceeds the
    payload limit.
    """

    pass
