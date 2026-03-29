from __future__ import annotations

import os
from typing import Any

from feishu_extension_skills.auth import AuthContext
from feishu_extension_skills.core.config import load_config
from feishu_extension_skills.core.errors import ValidationError
from pydantic import ValidationError as PydanticValidationError

from .client import ImChatAPIClient
from .models import (
    AddChatMembersInput,
    ChatMembersPage,
    ChatOperationResult,
    ChatSummary,
    CreateChatInput,
    DisbandChatInput,
    GetChatInput,
    ListChatMembersInput,
    RemoveChatMemberInput,
)


class ImChatService:
    def __init__(self, client: ImChatAPIClient | None = None) -> None:
        self._client = client or ImChatAPIClient()

    def create_chat(self, payload: CreateChatInput) -> ChatSummary:
        return self._client.create_chat(self._auth_context(payload), payload)

    def get_chat(self, payload: GetChatInput) -> ChatSummary:
        return self._client.get_chat(self._auth_context(payload), payload.chat_id)

    def disband_chat(self, payload: DisbandChatInput) -> ChatOperationResult:
        return self._call_with_auth("disband_chat", payload)

    def list_chat_members(self, payload: ListChatMembersInput) -> ChatMembersPage:
        return self._call_with_auth("list_chat_members", payload)

    def add_chat_members(self, payload: AddChatMembersInput) -> ChatOperationResult:
        return self._call_with_auth("add_chat_members", payload)

    def remove_chat_member(self, payload: RemoveChatMemberInput) -> ChatOperationResult:
        return self._call_with_auth("remove_chat_member", payload)

    @staticmethod
    def _auth_context(payload: Any) -> AuthContext:
        config = load_config(
            app_id=getattr(payload, "app_id", None),
            app_secret=getattr(payload, "app_secret", None),
            base_url=getattr(payload, "base_url", None),
            config_file=getattr(payload, "config_file", None),
            env=os.environ,
        )
        return AuthContext.from_config(config)

    def _call_with_auth(self, method_name: str, payload: Any) -> Any:
        method = getattr(self._client, method_name)
        auth_context = self._auth_context(payload)
        try:
            return method(auth_context, payload)
        except TypeError:
            return method(payload)


def _validate_and_build(payload_model, args: dict[str, Any]):
    try:
        return payload_model.model_validate(args)
    except PydanticValidationError as exc:
        raise ValidationError(str(exc)) from exc


def create_chat_action(args: dict[str, Any], service: ImChatService | None = None) -> dict[str, Any]:
    payload = _validate_and_build(CreateChatInput, args)
    result = (service or ImChatService()).create_chat(payload)
    return result.model_dump(exclude_none=True)


def get_chat_action(args: dict[str, Any], service: ImChatService | None = None) -> dict[str, Any]:
    payload = _validate_and_build(GetChatInput, args)
    result = (service or ImChatService()).get_chat(payload)
    return result.model_dump(exclude_none=True)


def disband_chat_action(args: dict[str, Any], service: ImChatService | None = None) -> dict[str, Any]:
    payload = _validate_and_build(DisbandChatInput, args)
    result = (service or ImChatService()).disband_chat(payload)
    return result.model_dump(exclude_none=True)


def list_chat_members_action(args: dict[str, Any], service: ImChatService | None = None) -> dict[str, Any]:
    payload = _validate_and_build(ListChatMembersInput, args)
    result = (service or ImChatService()).list_chat_members(payload)
    return result.model_dump(exclude_none=True)


def add_chat_members_action(args: dict[str, Any], service: ImChatService | None = None) -> dict[str, Any]:
    payload = _validate_and_build(AddChatMembersInput, args)
    result = (service or ImChatService()).add_chat_members(payload)
    return result.model_dump(exclude_none=True)


def remove_chat_member_action(args: dict[str, Any], service: ImChatService | None = None) -> dict[str, Any]:
    payload = _validate_and_build(RemoveChatMemberInput, args)
    result = (service or ImChatService()).remove_chat_member(payload)
    return result.model_dump(exclude_none=True)


__all__ = [
    "ImChatService",
    "add_chat_members_action",
    "create_chat_action",
    "disband_chat_action",
    "get_chat_action",
    "list_chat_members_action",
    "remove_chat_member_action",
]
