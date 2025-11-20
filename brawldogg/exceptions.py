class HTTPException(Exception):
    def __init__(self, status: int, reason: str, message: str):
        self.status = status
        self.reason = reason
        self.message = message
        super().__init__(f"{status} {reason}: {message}")


class BadRequest(HTTPException):
    """Raised for 400 Client provided incorrect parameters."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(400, reason, message)


class AccessDenied(HTTPException):
    """Raised for 403 missing/incorrect credentials or permissions issues."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(403, reason, message)


class NotFound(HTTPException):
    """Raised for 404 Resource not found."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(404, reason, message)


class RateLimited(HTTPException):
    """Raised for 429 Request throttled."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(429, reason, message)


class InternalServerError(HTTPException):
    """Raised for 500 Unknown error happened."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(500, reason, message)


class Unavailable(HTTPException):
    """Raised for 503 Service temporarily unavailable."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(503, reason, message)
