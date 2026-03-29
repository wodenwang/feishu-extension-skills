from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ALLOWED_MEMBER_ID_TYPES = {"user_id", "open_id"}
DEFAULT_BASE_URL = "https://open.feishu.cn"


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


class ImChatModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ChatAuthInput(ImChatModel):
    app_id: str | None = None
    app_secret: str | None = None
    config_file: str | None = None
    base_url: str = DEFAULT_BASE_URL


class CreateChatInput(ChatAuthInput):
    name: str
    user_id_list: list[str] = Field(default_factory=list)
    owner_id: str | None = None
    chat_mode: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name cannot be empty")
        return value

    @field_validator("user_id_list")
    @classmethod
    def validate_user_id_list(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("user_id_list cannot be empty")
        return _dedupe_preserve_order(cleaned)


class GetChatInput(ChatAuthInput):
    chat_id: str

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("chat_id cannot be empty")
        return value


class DisbandChatInput(ChatAuthInput):
    chat_id: str

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("chat_id cannot be empty")
        return value


class ListChatMembersInput(ChatAuthInput):
    chat_id: str
    page_size: int | None = None
    page_token: str | None = None
    member_id_type: str | None = "user_id"

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("chat_id cannot be empty")
        return value

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("page_size must be positive")
        return value

    @field_validator("member_id_type")
    @classmethod
    def validate_member_id_type(cls, value: str | None) -> str:
        normalized = (value or "user_id").strip()
        if normalized not in ALLOWED_MEMBER_ID_TYPES:
            raise ValueError("member_id_type must be user_id or open_id")
        return normalized


class AddChatMembersInput(ChatAuthInput):
    chat_id: str
    user_id_list: list[str] = Field(default_factory=list)
    member_id_type: str | None = "user_id"

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("chat_id cannot be empty")
        return value

    @field_validator("user_id_list")
    @classmethod
    def validate_user_id_list(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("user_id_list cannot be empty")
        return _dedupe_preserve_order(cleaned)

    @field_validator("member_id_type")
    @classmethod
    def validate_member_id_type(cls, value: str | None) -> str:
        normalized = (value or "user_id").strip()
        if normalized not in ALLOWED_MEMBER_ID_TYPES:
            raise ValueError("member_id_type must be user_id or open_id")
        return normalized


class RemoveChatMemberInput(ChatAuthInput):
    chat_id: str
    member_id: str
    member_id_type: str | None = "user_id"

    @field_validator("chat_id", "member_id")
    @classmethod
    def validate_required_identifier(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("identifier cannot be empty")
        return value

    @field_validator("member_id_type")
    @classmethod
    def validate_member_id_type(cls, value: str | None) -> str:
        normalized = (value or "user_id").strip()
        if normalized not in ALLOWED_MEMBER_ID_TYPES:
            raise ValueError("member_id_type must be user_id or open_id")
        return normalized


class ChatSummary(ImChatModel):
    chat_id: str
    name: str | None = None
    member_count: int | None = None
    owner_id: str | None = None
    description: str | None = None
    chat_mode: str | None = None
    avatar_url: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ChatMemberSummary(ImChatModel):
    member_id: str
    name: str | None = None
    member_id_type: str | None = None
    role: str | None = None
    avatar_url: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ChatMembersPage(ImChatModel):
    chat_id: str
    items: list[ChatMemberSummary] = Field(default_factory=list)
    has_more: bool = False
    page_token: str | None = None


class ChatOperationResult(ImChatModel):
    chat_id: str | None = None
    status: str = "ok"
    message: str | None = None
    added_member_ids: list[str] = Field(default_factory=list)
    failed_member_ids: list[str] = Field(default_factory=list)
    removed_member_id: str | None = None
    member_count: int | None = None
    chat: ChatSummary | None = None


class FeishuAPIEnvelope(ImChatModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    code: int | str = 0
    msg: str = "ok"
    data: dict[str, Any] | list[Any] | None = None
    request_id: str | None = None
    error: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, dict) and "data" not in value and "code" in value:
            return value
        if isinstance(value, dict):
            return {
                "code": value.get("code", 0),
                "msg": value.get("msg", "ok"),
                "data": value.get("data", value),
                "request_id": value.get("request_id"),
            }
        return value
