"""
Version 00 message marshalling/unmarshalling.
"""

from gotalk.protocol.defines import SINGLE_REQUEST_TYPE, SINGLE_RESULT_TYPE, \
    STREAM_REQUEST_TYPE, STREAM_REQUEST_PART_TYPE, STREAM_RESULT_TYPE, \
    ERROR_RESULT_TYPE, NOTIFICATION_TYPE


class GotalkMessage(object):
    """
    Doesn't do anything for now. We'll just set a common ancestor for the
    user's benefit.

    .. tip:: Don't use this class directly!
    """

    pass


class GotalkRequestMessage(GotalkMessage):
    pass


class GotalkResultMessage(GotalkMessage):
    pass


class ProtocolVersionMessage(GotalkMessage):
    """
    ProtocolVersion = <hexdigit> <hexdigit>
    """

    version = "00"

    def to_bytes(self):
        return self.version


class SingleRequestMessage(GotalkRequestMessage):
    """
    SingleRequest   = "r" requestID operation payload

    requestID       = <byte> <byte> <byte>
    operation       = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- SingleRequest
    |  +---------------- requestID   "001"
    |  |  +------------- text3Size   4
    |  |  |   +--------- operation   "echo"
    |  |  |   |       +- payloadSize 25
    |  |  |   |       |
    r001004echo00000019{"message":"Hello World"}
    """

    type_id = SINGLE_REQUEST_TYPE

    def __init__(self, request_id, operation, payload):
        self.request_id = request_id
        self.operation = operation
        self.payload = payload

    def to_bytes(self):
        text3_size = len(self.operation)
        payload_size = len(self.payload)
        return "{type_id}{request_id:03d}" \
               "{text3_size:03d}{operation}" \
               "{payload_size:08x}{payload}".format(
                type_id=self.type_id, request_id=self.request_id,
                text3_size=text3_size, operation=self.operation,
                payload_size=payload_size, payload=self.payload)

    @classmethod
    def from_bytes(cls, bytes):
        request_id = bytes[1:4]
        operation_length = int(bytes[4:7])
        operation_end = 7 + operation_length
        operation = bytes[7: operation_end]
        payload_size_end = operation_end + 8
        payload = bytes[payload_size_end:]
        return cls(request_id, operation, payload)


class SingleResultMessage(GotalkResultMessage):
    """
    SingleResult    = "R" requestID payload

    requestID       = <byte> <byte> <byte>
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- SingleResult
    |  +---------------- requestID   "001"
    |  |       +-------- payloadSize 25
    |  |       |
    R00100000019{"message":"Hello World"}
    """

    type_id = SINGLE_RESULT_TYPE

    def __init__(self, request_id, payload):
        self.request_id = request_id
        self.payload = payload

    def to_bytes(self):
        payload_size = len(self.payload)
        return "{type_id}{request_id:03d}{payload_size:08x}{payload}".format(
            type_id=self.type_id, request_id=self.request_id,
            payload_size=payload_size, payload=self.payload)


class StreamRequestMessage(GotalkRequestMessage):
    """
    StreamRequest   = "s" requestID operation payload StreamReqPart+

    requestID       = <byte> <byte> <byte>
    operation       = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}
    StreamReqPart   = "p" requestID payload

    +----------------- StreamRequest
    |  +---------------- requestID   "001"
    |  |      +--------- operation   "echo"
    |  |      |       +- payloadSize 25
    |  |      |       |
    s001004echo0000000b{"message":
    """

    type_id = STREAM_REQUEST_TYPE

    def __init__(self, request_id, operation, payload):
        self.request_id = request_id
        self.operation = operation
        self.payload = payload

    def to_bytes(self):
        text3_size = len(self.operation)
        payload_size = len(self.payload)
        return "{type_id}{request_id:03d}" \
               "{text3_size:03d}{operation}" \
               "{payload_size:08x}{payload}".format(
                type_id=self.type_id, request_id=self.request_id,
                text3_size=text3_size, operation=self.operation,
                payload_size=payload_size, payload=self.payload)


class StreamRequestPartMessage(GotalkRequestMessage):
    """
    StreamReqPart   = "p" requestID payload

    requestID       = <byte> <byte> <byte>
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- streamReqPart
    |  +---------------- requestID   "001"
    |  |       +-------- payloadSize 25
    |  |       |
    p0010000000e"Hello World"}
    """

    type_id = STREAM_REQUEST_PART_TYPE

    def __init__(self, request_id, payload):
        self.request_id = request_id
        self.payload = payload

    def to_bytes(self):
        payload_size = len(self.payload)
        return "{type_id}{request_id:03d}{payload_size:08x}{payload}".format(
                type_id=self.type_id, request_id=self.request_id,
                payload_size=payload_size, payload=self.payload)


class StreamResultMessage(GotalkResultMessage):
    """
    StreamResult    = "S" requestID payload StreamResult*

    requestID       = <byte> <byte> <byte>
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- StreamResult (1st part)
    |  +---------------- requestID   "001"
    |  |       +-------- payloadSize 25
    |  |       |
    S0010000000b{"message":
    """

    type_id = STREAM_RESULT_TYPE

    def __init__(self, request_id, payload):
        self.request_id = request_id
        self.payload = payload

    def to_bytes(self):
        payload_size = len(self.payload)
        return "{type_id}{request_id:03d}{payload_size:08x}{payload}".format(
            type_id=self.type_id, request_id=self.request_id,
            payload_size=payload_size, payload=self.payload)


class ErrorResultMessage(GotalkResultMessage):
    """
    ErrorResult     = "E" requestID payload

    requestID       = <byte> <byte> <byte>
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- ErrorResult
    |  +---------------- requestID   "001"
    |  |       +-------- payloadSize 38
    |  |       |
    E00100000026{"error":"Unknown operation \"echo\""}
    """

    type_id = ERROR_RESULT_TYPE

    def __init__(self, request_id, payload):
        self.request_id = request_id
        self.payload = payload

    def to_bytes(self):
        payload_size = len(self.payload)
        return "{type_id}{request_id:03d}{payload_size:08x}{payload}".format(
            type_id=self.type_id, request_id=self.request_id,
            payload_size=payload_size, payload=self.payload)


class NotificationMessage(GotalkMessage):
    """
    Notification    = "n" type payload

    type            = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +---------------------- Notification
    |              +--------- type        "chat message"
    |              |       +- payloadSize 50
    |              |       |
    n00cchat message00000032{"message":"Hi","from":"nthn","chat_room":"gonuts"}
    """

    type_id = NOTIFICATION_TYPE

    def __init__(self, n_type, payload):
        self.n_type = n_type
        self.payload = payload

    def to_bytes(self):
        payload_size = len(self.payload)
        return "{type_id}{n_type}{payload_size:08x}{payload}".format(
            type_id=self.type_id, n_type=self.n_type,
            payload_size=payload_size, payload=self.payload)
