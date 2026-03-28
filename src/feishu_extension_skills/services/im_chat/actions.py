from __future__ import annotations

from collections.abc import Callable
from typing import Any

from feishu_extension_skills.core.errors import FeishuAPIError, ValidationError
from pydantic import ValidationError as PydanticValidationError

from .client import ImChatAPIError, ImChatTransportError, ImChatValidationError
from .service import (
    ImChatService,
    add_chat_members_action,
    create_chat_action,
    disband_chat_action,
    get_chat_action,
    list_chat_members_action,
    remove_chat_member_action,
)

FEISHU_CHAT_CREATE = "feishu-chat-create"
FEISHU_CHAT_GET = "feishu-chat-get"
FEISHU_CHAT_DISBAND = "feishu-chat-disband"
FEISHU_CHAT_MEMBERS_LIST = "feishu-chat-members-list"
FEISHU_CHAT_MEMBER_ADD = "feishu-chat-member-add"
FEISHU_CHAT_MEMBER_REMOVE = "feishu-chat-member-remove"

ACTION_HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    FEISHU_CHAT_CREATE: create_chat_action,
    FEISHU_CHAT_GET: get_chat_action,
    FEISHU_CHAT_DISBAND: disband_chat_action,
    FEISHU_CHAT_MEMBERS_LIST: list_chat_members_action,
    FEISHU_CHAT_MEMBER_ADD: add_chat_members_action,
    FEISHU_CHAT_MEMBER_REMOVE: remove_chat_member_action,
}


def get_action_handler(action: str) -> Callable[..., dict[str, Any]]:
    try:
        return ACTION_HANDLERS[action]
    except KeyError as exc:
        raise KeyError(f"unknown action: {action}") from exc


def invoke_action(action: str, args: dict[str, Any], service: Any | None = None) -> dict[str, Any]:
    handler = get_action_handler(action)
    return handler(args, service=service)


def register_actions(registry: Any, service: ImChatService | None = None) -> None:
    registry.register(FEISHU_CHAT_CREATE, _wrap_handler(create_chat_action, service), description="Create a Feishu chat")
    registry.register(
        FEISHU_CHAT_GET,
        _wrap_handler(get_chat_action, service),
        description="Get details for a Feishu chat",
    )
    registry.register(
        FEISHU_CHAT_DISBAND,
        _wrap_handler(disband_chat_action, service),
        description="Disband a Feishu chat",
    )
    registry.register(
        FEISHU_CHAT_MEMBERS_LIST,
        _wrap_handler(list_chat_members_action, service),
        description="List members in a Feishu chat",
    )
    registry.register(
        FEISHU_CHAT_MEMBER_ADD,
        _wrap_handler(add_chat_members_action, service),
        description="Add members to a Feishu chat",
    )
    registry.register(
        FEISHU_CHAT_MEMBER_REMOVE,
        _wrap_handler(remove_chat_member_action, service),
        description="Remove a member from a Feishu chat",
    )


def _wrap_handler(handler: Callable[..., dict[str, Any]], service: ImChatService | None = None) -> Callable[[Any], dict[str, Any]]:
    def _inner(request: Any) -> dict[str, Any]:
        try:
            return handler(request.args, service=service)
        except PydanticValidationError as exc:
            raise ValidationError(str(exc)) from exc
        except ImChatValidationError as exc:
            raise ValidationError(str(exc)) from exc
        except ImChatTransportError as exc:
            raise FeishuAPIError(code="http_error", message=str(exc), details=getattr(exc, "details", None)) from exc
        except ImChatAPIError as exc:
            raise FeishuAPIError(
                code="feishu_api_error",
                message=str(exc),
                details=getattr(exc, "details", None),
            ) from exc

    return _inner


__all__ = [
    "ACTION_HANDLERS",
    "FEISHU_CHAT_CREATE",
    "FEISHU_CHAT_DISBAND",
    "FEISHU_CHAT_GET",
    "FEISHU_CHAT_MEMBER_ADD",
    "FEISHU_CHAT_MEMBER_REMOVE",
    "FEISHU_CHAT_MEMBERS_LIST",
    "get_action_handler",
    "invoke_action",
    "register_actions",
]
