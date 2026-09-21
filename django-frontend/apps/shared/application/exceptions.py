class StandardException(Exception):
    """Application-level exception (mapped to HTTP 400/500)."""

    status_code = 400
    default_message = "Application error"

    def __init__(self, message: str | None = None, *, code: str | None = None):
        self.message = message or self.default_message
        self.code = code
        super().__init__(self.message)


class DomainException(StandardException):
    """Domain rule violation."""

    status_code = 422
    default_message = "Domain rule violation"


class NotFoundException(StandardException):
    status_code = 404
    default_message = "Resource not found"


class UnauthorizedException(StandardException):
    status_code = 401
    default_message = "Unauthorized"
