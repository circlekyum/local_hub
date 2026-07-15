from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorItem(BaseModel):
    field: str
    message: str
    type: str


class ValidationErrorResponse(ErrorResponse):
    errors: list[ValidationErrorItem]
