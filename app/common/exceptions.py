class AppException(Exception):
    """Base application error mapped to an HTTP response by error handlers."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


class UnauthorizedException(AppException):
    def __init__(
        self,
        code: str = "UNAUTHORIZED",
        message: str = "Authentication required or invalid.",
    ) -> None:
        super().__init__(401, code, message)


class NotFoundException(AppException):
    def __init__(
        self,
        code: str = "NOT_FOUND",
        message: str = "Resource not found.",
    ) -> None:
        super().__init__(404, code, message)


class ConflictException(AppException):
    def __init__(self, code: str = "CONFLICT", message: str = "Conflict.") -> None:
        super().__init__(409, code, message)


class ForbiddenException(AppException):
    def __init__(self, code: str = "FORBIDDEN", message: str = "Forbidden.") -> None:
        super().__init__(403, code, message)


class BusinessRuleException(AppException):
    def __init__(
        self,
        code: str = "BUSINESS_RULE",
        message: str = "Request cannot be processed.",
    ) -> None:
        super().__init__(422, code, message)
