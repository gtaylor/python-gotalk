"""
Constants and other defines.
"""

# Various message type characters. These are the first byte in every message
# but the initial version exchange.
SINGLE_REQUEST_TYPE = "r"
SINGLE_RESULT_TYPE = "R"
STREAM_REQUEST_TYPE = "s"
STREAM_REQUEST_PART_TYPE = "p"
STREAM_RESULT_TYPE = "S"
ERROR_RESULT_TYPE = "E"
RETRY_RESULT_TYPE = "e"
NOTIFICATION_TYPE = "n"

# Maps the single-character message type ID to some standardized class names
# that we use for all versions of the protocol.
MESSAGE_TYPE_TO_CLASS_MAP = {
    SINGLE_REQUEST_TYPE: 'SingleRequestMessage',
    SINGLE_RESULT_TYPE: 'SingleResultMessage',
    STREAM_REQUEST_TYPE: 'StreamRequestMessage',
    STREAM_REQUEST_PART_TYPE: 'StreamRequestPartMessage',
    STREAM_RESULT_TYPE: 'StreamResultMessage',
    ERROR_RESULT_TYPE: 'ErrorResultMessage',
    RETRY_RESULT_TYPE: 'RetryResultMessage',
    NOTIFICATION_TYPE: 'NotificationMessage',
}
