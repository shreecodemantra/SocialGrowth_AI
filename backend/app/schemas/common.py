"""Common response envelopes."""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
