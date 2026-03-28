"""Runtime errors translated into frozen phase-1 error codes."""

from __future__ import annotations


class RuntimeErrorBase(Exception):
    code = "internal_error"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.details = details


class ConfigError(RuntimeErrorBase):
    code = "config_error"


class ValidationError(RuntimeErrorBase):
    code = "validation_error"


class ActionNotFoundError(RuntimeErrorBase):
    code = "action_not_found"


class FeishuAPIError(RuntimeErrorBase):
    code = "feishu_api_error"


class HTTPError(RuntimeErrorBase):
    code = "http_error"


class InternalError(RuntimeErrorBase):
    code = "internal_error"

