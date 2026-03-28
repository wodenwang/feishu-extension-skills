"""Input validation helpers for the runtime layer."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .errors import ValidationError
from .models import InvokeRequest


def parse_args_json(args_json: str | None) -> dict[str, Any]:
    if args_json is None or args_json == "":
        return {}

    try:
        data = json.loads(args_json)
    except json.JSONDecodeError as exc:
        raise ValidationError("invalid JSON passed to --args-json", details={"error": str(exc)}) from exc

    if not isinstance(data, dict):
        raise ValidationError("--args-json must decode to an object", details={"type": type(data).__name__})

    return data


def normalize_invoke_request(action: str, args: str | Mapping[str, Any] | None) -> InvokeRequest:
    if isinstance(args, str) or args is None:
        args_dict = parse_args_json(args)
    else:
        args_dict = dict(args)

    if not action or not action.strip():
        raise ValidationError("action is required")

    return InvokeRequest(action=action.strip(), args=args_dict)

