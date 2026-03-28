from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: dict[str, Any] | None = None


class ActionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    action: str
    data: dict[str, Any] | None = None
    error: ErrorPayload | None = None


def ok_result(action: str, data: dict[str, Any] | None = None) -> ActionResult:
    return ActionResult(ok=True, action=action, data=data or {}, error=None)


def error_result(
    action: str,
    code: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
) -> ActionResult:
    return ActionResult(
        ok=False,
        action=action,
        data=None,
        error=ErrorPayload(code=code, message=message, details=details),
    )
