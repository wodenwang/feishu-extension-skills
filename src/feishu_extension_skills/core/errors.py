from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class FeishuError(Exception):
    """Base class for first-phase Feishu errors."""


class ConfigError(FeishuError):
    """Raised when required configuration is missing or invalid."""


class ValidationError(FeishuError):
    """Raised when request payload validation fails."""


@dataclass(slots=True)
class FeishuAPIError(FeishuError):
    """Raised when Feishu returns a non-success response."""

    code: str
    message: str
    status_code: int | None = None
    request_id: str | None = None
    details: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def to_error_payload(self) -> dict[str, Any]:
        details: dict[str, Any] = dict(self.details or {})
        if self.status_code is not None:
            details["status_code"] = self.status_code
        if self.request_id is not None:
            details["request_id"] = self.request_id
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if details:
            payload["details"] = details
        return payload
