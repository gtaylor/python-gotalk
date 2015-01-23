"""
Version 00 message marshalling/unmarshalling.
"""

from gotalk.protocol.defines import SINGLE_REQUEST_TYPE, SINGLE_RESULT_TYPE, \
    STREAM_REQUEST_TYPE, STREAM_REQUEST_PART_TYPE, STREAM_RESULT_TYPE, \
    ERROR_RESULT_TYPE, NOTIFICATION_TYPE


class GotalkMessage(object):
    """
    .. tip:: Don't use this class directly!
    """

    protocol_version = "00"

    def _pad_request_id(self, request_id):
        return str(request_id).zfill(3)

    @classmethod
    def _get_reguest_id_from_bytes(cls, m_bytes):
        return m_bytes[1:4]

    @classmethod
    def _get_payload_from_bytes(cls, m_bytes, payload_size_start):
        payload_size_end = payload_size_start + 8
        return m_bytes[payload_size_end:]


class GotalkRequestMessage(GotalkMessage):
    """
    .. tip:: Don't use this class directly!
    """

    @classmethod
    def _get_operation_from_bytes(cls, m_bytes):
        operation_length = int(m_bytes[4:7], 16)
        operation_end = 7 + operation_length
        operation = m_bytes[7: operation_end]
        return operation, operation_end


class GotalkResultMessage(GotalkMessage):
    """
    .. tip:: Don't use this class directly!
    """

    pass


class ProtocolVersionMessage(GotalkMessage):
    """
    ProtocolVersion = <hexdigit> <hexdigit>
    """

    def to_bytes(self):
        return self.protocol_version


class SingleRequestMessage(GotalkRequestMessage):
    """
    SingleRequest   = "r" requestID operation payload

    requestID       = <byte> <byte> <byte>
    operation       = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    text3           = text3Size text3Value
    text3Size       = hexUInt3
    text3Value      = <<byte>{text3Size} as utf8 text>

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
        operation_size = len(self.operation)
        payload_size = len(self.payload)
        return "{type_id}{request_id}" \
               "{operation_size:03d}{operation}" \
               "{payload_size:08x}{payload}".format(
                type_id=self.type_id,
                request_id=self._pad_request_id(self.request_id),
                operation_size=operation_size, operation=self.operation,
                payload_size=payload_size, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        operation, operation_end = cls._get_operation_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, operation_end)
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
        return "{type_id}{request_id}{payload_size:08x}{payload}".format(
            type_id=self.type_id,
            request_id=self._pad_request_id(self.request_id),
            payload_size=payload_size, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, payload_size_start=4)
        return cls(request_id, payload)


class StreamRequestMessage(GotalkRequestMessage):
    """
    StreamRequest   = "s" requestID operation payload StreamReqPart+

    requestID       = <byte> <byte> <byte>
    operation       = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}
    StreamReqPart   = "p" requestID payload

    text3           = text3Size text3Value
    text3Size       = hexUInt3
    text3Value      = <<byte>{text3Size} as utf8 text>

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
        operation_size = len(self.operation)
        payload_size = len(self.payload)
        return "{type_id}{request_id}" \
               "{operation_size:03d}{operation}" \
               "{payload_size:08x}{payload}".format(
                type_id=self.type_id,
                request_id=self._pad_request_id(self.request_id),
                operation_size=operation_size, operation=self.operation,
                payload_size=payload_size, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        operation, operation_end = cls._get_operation_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, operation_end)
        return cls(request_id, operation, payload)


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
        return "{type_id}{request_id}{payload_size:08x}{payload}".format(
                type_id=self.type_id,
                request_id=self._pad_request_id(self.request_id),
                payload_size=payload_size, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, payload_size_start=4)
        return cls(request_id, payload)


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
        return "{type_id}{request_id}{payload_size:08x}{payload}".format(
            type_id=self.type_id,
            request_id=self._pad_request_id(self.request_id),
            payload_size=payload_size, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, payload_size_start=4)
        return cls(request_id, payload)


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
        return "{type_id}{request_id}{payload_size:08x}{payload}".format(
            type_id=self.type_id,
            request_id=self._pad_request_id(self.request_id),
            payload_size=payload_size, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, payload_size_start=4)
        return cls(request_id, payload)


class NotificationMessage(GotalkMessage):
    """
    Notification    = "n" type payload

    type            = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    text3           = text3Size text3Value
    text3Size       = hexUInt3
    text3Value      = <<byte>{text3Size} as utf8 text>

    +---------------------- Notification
    |  +--------------------- text3Size   12
    |  |           +--------- type        "chat message"
    |  |           |       +- payloadSize 50
    |  |           |       |
    n00cchat message00000032{"message":"Hi","from":"nthn","chat_room":"gonuts"}
    """

    type_id = NOTIFICATION_TYPE

    def __init__(self, n_type, payload):
        self.n_type = n_type
        self.payload = payload

    def to_bytes(self):
        n_type_size = len(self.n_type)
        payload_size = len(self.payload)
        return "{type_id}{n_type_size:03x}{n_type}{payload_size:08x}{payload}".format(
            type_id=self.type_id, n_type_size=n_type_size, n_type=self.n_type,
            payload_size=payload_size, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        n_type = cls._get_n_type_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, payload_size_start=4)
        return cls(n_type, payload)

    @classmethod
    def _get_n_type_from_bytes(cls, m_bytes):
        n_type_length = int(m_bytes[1:4], 16)
        n_type_end = 4 + n_type_length
        n_type = m_bytes[4: n_type_end]
        return n_type, n_type_end
