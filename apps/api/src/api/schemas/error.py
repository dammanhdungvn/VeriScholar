from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    field: str | None = Field(default=None, description="Field name if validation error")
    action: str | None = Field(default=None, description="Actionable step to resolve the error")


class ErrorResponse(BaseModel):
    success: bool = Field(default=False)
    error: ErrorDetail
    meta: dict[str, Any] = Field(default_factory=dict)
