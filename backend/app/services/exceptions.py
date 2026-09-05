"""Domain-level exceptions, translated to HTTP responses in the API layer."""


class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    status_code: int = 400
    retryable: bool = False

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AlreadyExistsError(DomainError):
    code = "ALREADY_EXISTS"
    status_code = 409


class NotFoundError(DomainError):
    code = "NOT_FOUND"
    status_code = 404


class InvalidCredentialsError(DomainError):
    code = "INVALID_CREDENTIALS"
    status_code = 401


class PermissionDeniedError(DomainError):
    code = "PERMISSION_DENIED"
    status_code = 403
