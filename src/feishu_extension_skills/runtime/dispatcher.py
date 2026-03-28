"""Action registry and dispatcher for phase-1 actions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable

from pydantic import ValidationError as PydanticValidationError

from feishu_extension_skills.core.errors import (
    ConfigError as CoreConfigError,
    FeishuAPIError as CoreFeishuAPIError,
    ValidationError as CoreValidationError,
)

from .errors import ActionNotFoundError, InternalError, RuntimeErrorBase, ValidationError
from .models import ActionResult, ErrorPayload, InvokeRequest, RegisteredAction
from .validators import normalize_invoke_request

ActionHandler = Callable[[InvokeRequest], Any]
DefaultLoader = Callable[["ActionRegistry"], None]


def _to_mapping(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        dumped = value.model_dump()
        return dict(dumped) if isinstance(dumped, Mapping) else {"value": dumped}
    if hasattr(value, "__dict__") and not isinstance(value, (str, bytes)):
        return dict(value.__dict__)
    return {"value": value}


def _result_from_error(action: str, exc: RuntimeErrorBase) -> ActionResult:
    details = exc.details if exc.details is not None else None
    return ActionResult(
        ok=False,
        action=action,
        data=None,
        error=ErrorPayload(code=exc.code, message=str(exc), details=details),
    )


def _result_from_exception(action: str, exc: Exception) -> ActionResult:
    return ActionResult(
        ok=False,
        action=action,
        data=None,
        error=ErrorPayload(
            code="internal_error",
            message="unexpected internal error",
            details={"exception": exc.__class__.__name__, "message": str(exc)},
        ),
    )


def _result_from_core_exception(action: str, exc: Exception) -> ActionResult:
    if isinstance(exc, CoreConfigError):
        return ActionResult(
            ok=False,
            action=action,
            data=None,
            error=ErrorPayload(code="config_error", message=str(exc), details=None),
        )

    if isinstance(exc, (CoreValidationError, PydanticValidationError)):
        details = exc.errors() if isinstance(exc, PydanticValidationError) else None
        return ActionResult(
            ok=False,
            action=action,
            data=None,
            error=ErrorPayload(code="validation_error", message=str(exc), details=details),
        )

    if isinstance(exc, CoreFeishuAPIError):
        code = "http_error" if exc.code == "http_error" else "feishu_api_error"
        return ActionResult(
            ok=False,
            action=action,
            data=None,
            error=ErrorPayload(code=code, message=exc.message, details=exc.to_error_payload().get("details")),
        )

    raise TypeError(f"unsupported core exception: {exc.__class__.__name__}")


def _wrap_action_result(action: str, payload: Any) -> ActionResult:
    if isinstance(payload, ActionResult):
        if payload.action == action:
            return payload
        return payload.model_copy(update={"action": action})

    data = _to_mapping(payload)
    return ActionResult(ok=True, action=action, data=data, error=None)


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, RegisteredAction] = {}
        self._default_actions_loaded = False

    def register(self, name: str, handler: ActionHandler, description: str | None = None) -> RegisteredAction:
        normalized = name.strip()
        if not normalized:
            raise ValidationError("action name is required")
        if normalized in self._actions:
            raise ValidationError(f"action already registered: {normalized}")

        registered = RegisteredAction(name=normalized, handler=handler, description=description)
        self._actions[normalized] = registered
        return registered

    def get(self, name: str) -> RegisteredAction | None:
        return self._actions.get(name.strip())

    def items(self) -> dict[str, RegisteredAction]:
        return dict(self._actions)

    def ensure_default_actions_loaded(self, loader: DefaultLoader | None = None) -> None:
        if self._default_actions_loaded:
            return
        self._default_actions_loaded = True

        loader = loader or load_default_actions
        loader(self)


def load_default_actions(registry: ActionRegistry) -> None:
    try:
        from feishu_extension_skills.services.im_chat.actions import register_actions
    except Exception:  # pragma: no cover - im_chat may not be implemented yet
        return

    register_actions(registry)


class ActionDispatcher:
    def __init__(self, registry: ActionRegistry | None = None, *, loader: DefaultLoader | None = None) -> None:
        self.registry = registry or ActionRegistry()
        self._loader = loader or load_default_actions

    def register(self, name: str, handler: ActionHandler, description: str | None = None) -> RegisteredAction:
        return self.registry.register(name, handler, description=description)

    def dispatch(self, request: InvokeRequest | str | Mapping[str, Any], args: Mapping[str, Any] | None = None) -> ActionResult:
        if isinstance(request, InvokeRequest):
            action_name = request.action
        elif isinstance(request, str):
            action_name = request
        elif isinstance(request, Mapping):
            action_name = str(request.get("action", "<unknown>"))
        else:
            action_name = "<unknown>"

        try:
            if isinstance(request, InvokeRequest):
                invoke_request = request
            elif isinstance(request, str):
                invoke_request = normalize_invoke_request(request, args)
            elif isinstance(request, Mapping):
                action = request.get("action", "")
                raw_args = request.get("args", args)
                invoke_request = normalize_invoke_request(str(action), raw_args)
            else:
                raise ValidationError("unsupported invoke request payload")

            action_name = invoke_request.action
            handler = self._resolve_handler(invoke_request.action)
            payload = handler(invoke_request)
            return _wrap_action_result(invoke_request.action, payload)
        except RuntimeErrorBase as exc:
            return _result_from_error(action_name, exc)
        except (CoreConfigError, CoreValidationError, CoreFeishuAPIError, PydanticValidationError) as exc:
            return _result_from_core_exception(action_name, exc)
        except Exception as exc:  # pragma: no cover - defensive guard
            return _result_from_exception(action_name, exc)

    def invoke(self, action: str, args: Mapping[str, Any] | str | None = None) -> ActionResult:
        return self.dispatch(action, args)

    def _resolve_handler(self, action: str) -> ActionHandler:
        registered = self.registry.get(action)
        if registered is None:
            self.registry.ensure_default_actions_loaded(self._loader)
            registered = self.registry.get(action)
        if registered is None:
            raise ActionNotFoundError(f"unknown action: {action}")
        return registered.handler


_default_dispatcher = ActionDispatcher()


def get_dispatcher() -> ActionDispatcher:
    return _default_dispatcher


def register_action(name: str, handler: ActionHandler, description: str | None = None) -> RegisteredAction:
    return _default_dispatcher.register(name, handler, description=description)


def dispatch(action: str, args: Mapping[str, Any] | str | None = None) -> ActionResult:
    return _default_dispatcher.invoke(action, args)
