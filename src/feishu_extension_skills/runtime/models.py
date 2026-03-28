"""Runtime data models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field

try:  # pragma: no cover - the core module is added by another phase-1 worker
    from feishu_extension_skills.core.result import ActionResult, ErrorPayload
except Exception:  # pragma: no cover
    class ErrorPayload(BaseModel):
        code: str
        message: str
        details: dict[str, Any] | None = None

    class ActionResult(BaseModel):
        ok: bool
        action: str
        data: dict[str, Any] | None = None
        error: ErrorPayload | None = None


class AuthArgs(BaseModel):
    model_config = ConfigDict(extra="ignore")

    app_id: str | None = None
    app_secret: str | None = None
    base_url: str | None = None


class InvokeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    args: dict[str, Any] = Field(default_factory=dict)


@dataclass(slots=True)
class RegisteredAction:
    name: str
    handler: Callable[[InvokeRequest], Any]
    description: str | None = None

