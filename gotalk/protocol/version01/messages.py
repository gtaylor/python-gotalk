"""
Version 00 message marshalling/unmarshalling.
"""

from gotalk.exceptions import PayloadTooLongError, OperationTooLongError
from gotalk.protocol.defines import SINGLE_REQUEST_TYPE, SINGLE_RESULT_TYPE, \
    STREAM_REQUEST_TYPE, STREAM_REQUEST_PART_TYPE, STREAM_RESULT_TYPE, \
    ERROR_RESULT_TYPE, NOTIFICATION_TYPE, RETRY_RESULT_TYPE


class GotalkMessage(object):
    """
    .. tip:: Don't use this class directly!
    """

    protocol_version = "01"
    payload_max_length = 4294967295

    _request_id_start = 1
    _request_id_end = 5
    _payload_length_bytes = 8

    def _pad_request_id(self, request_id):
        return str(request_id).zfill(3)

    def _check_payload_length(self, payload):
        payload_length = len(payload)
        if payload_length > self.payload_max_length:
            raise PayloadTooLongError(
                "Payload length limit exceeded. Must be < 4 GB.")
        return payload_length

    @classmethod
    def _get_reguest_id_from_bytes(cls, m_bytes):
        return m_bytes[cls._request_id_start:cls._request_id_end]

    @classmethod
    def _get_payload_from_bytes(cls, m_bytes, payload_length_start):
        payload_length_end = payload_length_start + cls._payload_length_bytes
        return m_bytes[payload_length_end:]


class GotalkRequestMessage(GotalkMessage):
    """
    .. tip:: Don't use this class directly!
    """

    operation_max_length = 4095

    _operation_length_bytes = 3
    _operation_length_start = GotalkMessage._request_id_end
    _operation_length_end = GotalkMessage._request_id_end + _operation_length_bytes

    def _check_operation_length(self, operation):
        operation_length = len(operation)
        if operation_length > self.operation_max_length:
            raise OperationTooLongError(
                "Operation length limit exceeded. Must be < 4 KB.")
        return operation_length

    @classmethod
    def _get_operation_from_bytes(cls, m_bytes):
        op_length_hex = m_bytes[cls._operation_length_start:cls._operation_length_end]
        operation_length = int(op_length_hex, 16)
        operation_end = cls._operation_length_end + operation_length
        operation = m_bytes[cls._operation_length_end: operation_end]
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

    requestID       = <byte> <byte> <byte> <byte>
    operation       = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    text3           = text3Size text3Value
    text3Size       = hexUInt3
    text3Value      = <<byte>{text3Size} as utf8 text>

    +----------------- SingleRequest
    |  +---------------- requestID   "0001"
    |  |  +------------- text3Size   4
    |  |  |   +--------- operation   "echo"
    |  |  |   |       +- payloadSize 25
    |  |  |   |       |
    r0001004echo00000019{"message":"Hello World"}
    """

    type_id = SINGLE_REQUEST_TYPE

    def __init__(self, request_id, operation, payload):
        self.request_id = request_id
        self.operation = operation
        self.payload = payload

    def to_bytes(self):
        operation_length = self._check_operation_length(self.operation)
        payload_length = self._check_payload_length(self.payload)
        return "{type_id}{request_id}" \
               "{operation_length:03d}{operation}" \
               "{payload_length:08x}{payload}".format(
                type_id=self.type_id,
                request_id=self._pad_request_id(self.request_id),
                operation_length=operation_length, operation=self.operation,
                payload_length=payload_length, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        operation, operation_end = cls._get_operation_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, operation_end)
        return cls(request_id, operation, payload)


class SingleResultMessage(GotalkResultMessage):
    """
    SingleResult    = "R" requestID payload

    requestID       = <byte> <byte> <byte> <byte>
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- SingleResult
    |  +---------------- requestID   "0001"
    |  |       +-------- payloadSize 25
    |  |       |
    R000100000019{"message":"Hello World"}
    """

    type_id = SINGLE_RESULT_TYPE

    def __init__(self, request_id, payload):
        self.request_id = request_id
        self.payload = payload

    def to_bytes(self):
        payload_length = self._check_payload_length(self.payload)
        return "{type_id}{request_id}{payload_length:08x}{payload}".format(
            type_id=self.type_id,
            request_id=self._pad_request_id(self.request_id),
            payload_length=payload_length, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(
            m_bytes, payload_length_start=cls._request_id_end)
        return cls(request_id, payload)


class StreamRequestMessage(GotalkRequestMessage):
    """
    StreamRequest   = "s" requestID operation payload StreamReqPart+

    requestID       = <byte> <byte> <byte> <byte>
    operation       = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}
    StreamReqPart   = "p" requestID payload

    text3           = text3Size text3Value
    text3Size       = hexUInt3
    text3Value      = <<byte>{text3Size} as utf8 text>

    +----------------- StreamRequest
    |  +---------------- requestID   "0001"
    |  |      +--------- operation   "echo"
    |  |      |       +- payloadSize 25
    |  |      |       |
    s0001004echo0000000b{"message":
    """

    type_id = STREAM_REQUEST_TYPE

    def __init__(self, request_id, operation, payload):
        self.request_id = request_id
        self.operation = operation
        self.payload = payload

    def to_bytes(self):
        operation_length = self._check_operation_length(self.operation)
        payload_length = self._check_payload_length(self.payload)
        return "{type_id}{request_id}" \
               "{operation_length:03d}{operation}" \
               "{payload_length:08x}{payload}".format(
                type_id=self.type_id,
                request_id=self._pad_request_id(self.request_id),
                operation_length=operation_length, operation=self.operation,
                payload_length=payload_length, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        operation, operation_end = cls._get_operation_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(m_bytes, operation_end)
        return cls(request_id, operation, payload)


class StreamRequestPartMessage(GotalkRequestMessage):
    """
    StreamReqPart   = "p" requestID payload

    requestID       = <byte> <byte> <byte> <byte>
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- streamReqPart
    |  +---------------- requestID   "0001"
    |  |       +-------- payloadSize 25
    |  |       |
    p00010000000e"Hello World"}
    """

    type_id = STREAM_REQUEST_PART_TYPE

    def __init__(self, request_id, payload):
        self.request_id = request_id
        self.payload = payload

    def to_bytes(self):
        payload_length = self._check_payload_length(self.payload)
        return "{type_id}{request_id}{payload_length:08x}{payload}".format(
                type_id=self.type_id,
                request_id=self._pad_request_id(self.request_id),
                payload_length=payload_length, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(
            m_bytes, payload_length_start=cls._request_id_end)
        return cls(request_id, payload)


class StreamResultMessage(GotalkResultMessage):
    """
    StreamResult    = "S" requestID payload StreamResult*

    requestID       = <byte> <byte> <byte> <byte>
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- StreamResult (1st part)
    |  +---------------- requestID   "0001"
    |  |       +-------- payloadSize 25
    |  |       |
    S00010000000b{"message":
    """

    type_id = STREAM_RESULT_TYPE

    def __init__(self, request_id, payload):
        self.request_id = request_id
        self.payload = payload

    def to_bytes(self):
        payload_length = self._check_payload_length(self.payload)
        return "{type_id}{request_id}{payload_length:08x}{payload}".format(
            type_id=self.type_id,
            request_id=self._pad_request_id(self.request_id),
            payload_length=payload_length, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(
            m_bytes, payload_length_start=cls._request_id_end)
        return cls(request_id, payload)


class ErrorResultMessage(GotalkResultMessage):
    """
    ErrorResult     = "E" requestID payload

    requestID       = <byte> <byte> <byte> <byte>
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +----------------- ErrorResult
    |  +---------------- requestID   "0001"
    |  |       +-------- payloadSize 38
    |  |       |
    E000100000026{"error":"Unknown operation \"echo\""}
    """

    type_id = ERROR_RESULT_TYPE

    def __init__(self, request_id, payload):
        self.request_id = request_id
        self.payload = payload

    def to_bytes(self):
        payload_length = self._check_payload_length(self.payload)
        return "{type_id}{request_id}{payload_length:08x}{payload}".format(
            type_id=self.type_id,
            request_id=self._pad_request_id(self.request_id),
            payload_length=payload_length, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(
            m_bytes, payload_length_start=cls._request_id_end)
        return cls(request_id, payload)


class RetryResultMessage(GotalkResultMessage):
    """
    RetryResult     = "e" requestID wait payload

    requestID       = <byte> <byte> <byte> <byte>
    wait            = hexUInt8
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    +-------------------- RetryResult
    |   +------------------ requestID   "0001"
    |   |       +---------- wait        0
    |   |       |       +-- payloadSize 20
    |   |       |       |
    e00010000000000000014"service restarting"
    """

    type_id = RETRY_RESULT_TYPE
    _wait_bytes = 8
    _wait_start = GotalkRequestMessage._request_id_end
    _wait_end = GotalkRequestMessage._request_id_end + _wait_bytes

    def __init__(self, request_id, wait, payload):
        self.request_id = request_id
        if not isinstance(wait, int):
            raise ValueError("wait value must be an int.")
        self.wait = wait
        self.payload = payload

    def to_bytes(self):
        payload_length = self._check_payload_length(self.payload)
        return "{type_id}{request_id}{wait:08x}{payload_length:08x}{payload}".format(
            type_id=self.type_id,
            request_id=self._pad_request_id(self.request_id),
            wait=self.wait, payload_length=payload_length, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        request_id = cls._get_reguest_id_from_bytes(m_bytes)
        wait = cls._get_wait_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(
            m_bytes, payload_length_start=cls._wait_end)
        return cls(request_id, wait, payload)

    @classmethod
    def _get_wait_from_bytes(cls, m_bytes):
        return int(m_bytes[cls._wait_start: cls._wait_end], 16)


class NotificationMessage(GotalkMessage):
    """
    Notification    = "n" name payload

    name            = text3
    payload         = payloadSize payloadData?
    payloadSize     = hexUInt8
    payloadData     = <byte>{payloadSize}

    text3           = text3Size text3Value
    text3Size       = hexUInt3
    text3Value      = <<byte>{text3Size} as utf8 text>

    +---------------------- Notification
    |  +--------------------- text3Size   12
    |  |           +--------- name        "chat message"
    |  |           |       +- payloadSize 50
    |  |           |       |
    n00cchat message00000032{"message":"Hi","from":"nthn","chat_room":"gonuts"}
    """

    type_id = NOTIFICATION_TYPE

    def __init__(self, name, payload):
        self.name = name
        self.payload = payload

    def to_bytes(self):
        name_size = len(self.name)
        payload_length = self._check_payload_length(self.payload)
        return "{type_id}{name_size:03x}{name}{payload_length:08x}{payload}".format(
            type_id=self.type_id, name_size=name_size, name=self.name,
            payload_length=payload_length, payload=self.payload)

    @classmethod
    def from_bytes(cls, m_bytes):
        name, name_end = cls._get_name_from_bytes(m_bytes)
        payload = cls._get_payload_from_bytes(
            m_bytes, payload_length_start=name_end)
        return cls(name, payload)

    @classmethod
    def _get_name_from_bytes(cls, m_bytes):
        name_length = int(m_bytes[1:4], 16)
        name_end = 4 + name_length
        name = m_bytes[4: name_end]
        return name, name_end
