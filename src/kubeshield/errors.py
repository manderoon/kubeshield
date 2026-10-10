class KubeshieldError(Exception):
    """
    Raised when a call fails
    The server returns it as {"detail": <message>} with status_code
    """

    status_code = 500


class UpstreamError(KubeshieldError):
    """Something ran but returned an error"""

    status_code = 502


class UnavailableError(KubeshieldError):
    """Something can't be reached"""

    status_code = 503


class UpstreamTimeoutError(KubeshieldError):
    """Something took too long"""

    status_code = 504
