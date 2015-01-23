"""
General, non-protocol-version-specific exceptions.
"""


class InvalidProtocolVersionError(Exception):
    pass


class InvalidMessageTypeIDError(Exception):
    pass
