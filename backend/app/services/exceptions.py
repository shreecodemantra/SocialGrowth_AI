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


class ValidationFailedError(DomainError):
    code = "VALIDATION_FAILED"
    status_code = 422


class GenerationFailedError(DomainError):
    """Raised when the AI content/image pipeline fails partway through. The
    partially-created Campaign/Post rows are kept (marked FAILED) so the
    caller can see what happened rather than losing the attempt."""

    code = "GENERATION_FAILED"
    status_code = 502
    retryable = True
