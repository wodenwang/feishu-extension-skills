from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urljoin

import httpx

from feishu_extension_skills.auth import AuthContext

from .models import (
    AddChatMembersInput,
    ChatMemberSummary,
    ChatMembersPage,
    ChatOperationResult,
    ChatSummary,
    CreateChatInput,
    DEFAULT_BASE_URL,
    DeleteChatInput,
    FeishuAPIEnvelope,
    ListChatMembersInput,
    RemoveChatMemberInput,
)

CHAT_CREATE_PATH = "/open-apis/im/v1/chats"
CHAT_DETAIL_PATH = "/open-apis/im/v1/chats/{chat_id}"
CHAT_MEMBERS_PATH = "/open-apis/im/v1/chats/{chat_id}/members"
CHAT_MEMBER_PATH = "/open-apis/im/v1/chats/{chat_id}/members/{member_id}"


class ImChatError(RuntimeError):
    """Base error for first-phase IM chat operations."""


class ImChatValidationError(ImChatError):
    """Raised when input data is invalid."""


class ImChatAPIError(ImChatError):
    """Raised when Feishu returns an API error payload."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class ImChatTransportError(ImChatError):
    """Raised when HTTP transport fails."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


def get_auth_headers(auth_context: Any) -> dict[str, str]:
    try:
        from feishu_extension_skills.auth.token_manager import get_auth_headers as auth_get_auth_headers
    except Exception as exc:  # pragma: no cover - import wiring depends on other agents
        raise RuntimeError("auth.get_auth_headers is not available yet") from exc
    return auth_get_auth_headers(auth_context)


def build_http_client(base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0) -> httpx.Client:
    try:
        from feishu_extension_skills.core.http import build_http_client as core_build_http_client
    except Exception:  # pragma: no cover - import wiring depends on other agents
        return httpx.Client(base_url=base_url, timeout=timeout)

    try:
        client = core_build_http_client(base_url=base_url, timeout_seconds=timeout)
    except Exception:
        return httpx.Client(base_url=base_url, timeout=timeout)

    if client is None or not hasattr(client, "request"):
        return httpx.Client(base_url=base_url, timeout=timeout)
    return client


class ImChatAPIClient:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        http_client: httpx.Client | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http_client = http_client or build_http_client(base_url=self.base_url, timeout=timeout)
        self._owns_client = http_client is None

    def close(self) -> None:
        if self._owns_client and hasattr(self._http_client, "close"):
            self._http_client.close()

    def __enter__(self) -> "ImChatAPIClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def create_chat(self, auth_context: Any, payload: CreateChatInput) -> ChatSummary:
        body: dict[str, Any] = {
            "name": payload.name,
            "user_id_list": payload.user_id_list,
        }
        if payload.owner_id is not None:
            body["owner_id"] = payload.owner_id
        if payload.chat_mode is not None:
            body["chat_mode"] = payload.chat_mode
        if payload.description is not None:
            body["description"] = payload.description

        response_data = self._request("POST", CHAT_CREATE_PATH, auth_context, json=body)
        summary = self._parse_chat_summary(response_data)
        if summary.chat_id:
            try:
                summary = self.get_chat(auth_context, summary.chat_id, fallback=summary)
            except ImChatError:
                pass
        return summary

    def get_chat(self, auth_context: Any, chat_id: str, *, fallback: ChatSummary | None = None) -> ChatSummary:
        response_data = self._request("GET", CHAT_DETAIL_PATH.format(chat_id=chat_id), auth_context)
        summary = self._parse_chat_summary(response_data)
        if summary.chat_id:
            return summary
        if fallback is not None:
            return fallback
        return ChatSummary(chat_id=chat_id)

    def delete_chat(
        self,
        auth_context: AuthContext | DeleteChatInput,
        payload: DeleteChatInput | None = None,
    ) -> ChatOperationResult:
        auth_context, payload = self._resolve_auth_and_payload(auth_context, payload)
        response_data = self._request("DELETE", CHAT_DETAIL_PATH.format(chat_id=payload.chat_id), auth_context)
        member_count = self._extract_int(response_data, ("member_count",))
        return ChatOperationResult(chat_id=payload.chat_id, status="deleted", member_count=member_count)

    def list_chat_members(
        self,
        auth_context: AuthContext | ListChatMembersInput,
        payload: ListChatMembersInput | None = None,
    ) -> ChatMembersPage:
        auth_context, payload = self._resolve_auth_and_payload(auth_context, payload)
        response_data = self._request(
            "GET",
            CHAT_MEMBERS_PATH.format(chat_id=payload.chat_id),
            auth_context,
            params=self._compact_dict(
                {
                    "page_size": payload.page_size,
                    "page_token": payload.page_token,
                    "member_id_type": payload.member_id_type,
                }
            ),
        )
        items = self._extract_member_items(response_data)
        return ChatMembersPage(
            chat_id=payload.chat_id,
            items=items,
            has_more=bool(self._extract_value(response_data, ("has_more", "has_more_data"), default=False)),
            page_token=self._extract_value(response_data, ("page_token", "next_page_token")),
        )

    def add_chat_members(
        self,
        auth_context: AuthContext | AddChatMembersInput,
        payload: AddChatMembersInput | None = None,
    ) -> ChatOperationResult:
        auth_context, payload = self._resolve_auth_and_payload(auth_context, payload)
        response_data = self._request(
            "POST",
            CHAT_MEMBERS_PATH.format(chat_id=payload.chat_id),
            auth_context,
            json=self._compact_dict(
                {
                    "id_list": payload.user_id_list,
                }
            ),
            params=self._compact_dict({"member_id_type": payload.member_id_type}),
        )
        invalid_ids = self._extract_string_list(
            response_data,
            ("invalid_id_list", "failed_member_ids", "not_existed_id_list", "pending_approval_id_list"),
        )
        added_ids = [member_id for member_id in payload.user_id_list if member_id not in invalid_ids]
        member_count = self._extract_int(response_data, ("member_count",))
        return ChatOperationResult(
            chat_id=payload.chat_id,
            status="ok",
            added_member_ids=added_ids,
            failed_member_ids=invalid_ids,
            member_count=member_count,
        )

    def remove_chat_member(
        self,
        auth_context: AuthContext | RemoveChatMemberInput,
        payload: RemoveChatMemberInput | None = None,
    ) -> ChatOperationResult:
        auth_context, payload = self._resolve_auth_and_payload(auth_context, payload)
        response_data = self._request(
            "DELETE",
            CHAT_MEMBERS_PATH.format(chat_id=payload.chat_id),
            auth_context,
            json=self._compact_dict({"id_list": [payload.member_id]}),
            params=self._compact_dict({"member_id_type": payload.member_id_type}),
        )
        removed_ids = self._extract_string_list(response_data, ("removed_member_ids", "removed_member_id", "member_id"))
        member_count = self._extract_int(response_data, ("member_count",))
        return ChatOperationResult(
            chat_id=payload.chat_id,
            status="ok",
            removed_member_id=removed_ids[0] if removed_ids else payload.member_id,
            member_count=member_count,
        )

    def _request(
        self,
        method: str,
        path: str,
        auth_context: Any,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        headers = dict(get_auth_headers(auth_context))
        if json is not None:
            headers.setdefault("Content-Type", "application/json")

        url = urljoin(self.base_url + "/", path.lstrip("/"))
        try:
            response = self._http_client.request(method, url, headers=headers, params=params, json=json)
        except httpx.HTTPError as exc:
            raise ImChatTransportError(str(exc), details={"method": method, "url": url}) from exc

        return self._parse_response(response)

    @staticmethod
    def _resolve_auth_and_payload(
        auth_context: AuthContext | Any,
        payload: Any | None,
    ) -> tuple[AuthContext, Any]:
        if payload is None:
            payload = auth_context
            auth_context = AuthContext(
                app_id=payload.app_id,
                app_secret=payload.app_secret,
                base_url=getattr(payload, "base_url", None) or DEFAULT_BASE_URL,
            )
        return auth_context, payload

    def _parse_response(self, response: httpx.Response) -> dict[str, Any] | list[Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise ImChatAPIError(
                "Feishu returned a non-JSON response",
                details={"status_code": response.status_code, "text": response.text},
            ) from exc

        if not isinstance(payload, dict):
            return payload

        envelope = FeishuAPIEnvelope.model_validate(payload)
        if response.status_code < 200 or response.status_code >= 300:
            raise ImChatAPIError(
                envelope.msg,
                details={
                    "status_code": response.status_code,
                    "code": envelope.code,
                    "msg": envelope.msg,
                    "request_id": envelope.request_id,
                    "payload": payload,
                },
            )
        if str(envelope.code) not in {"0", "200"}:
            raise ImChatAPIError(
                envelope.msg,
                details={
                    "code": envelope.code,
                    "msg": envelope.msg,
                    "request_id": envelope.request_id,
                    "payload": payload,
                },
            )
        return envelope.data if envelope.data is not None else payload

    def _parse_chat_summary(self, data: dict[str, Any] | list[Any]) -> ChatSummary:
        if isinstance(data, list):
            data = data[0] if data else {}

        if not isinstance(data, dict):
            return ChatSummary(chat_id="")

        chat_data = data.get("chat") if isinstance(data.get("chat"), dict) else data
        chat_id = self._extract_value(chat_data, ("chat_id", "id"), default="")
        return ChatSummary(
            chat_id=chat_id,
            name=self._extract_value(chat_data, ("name",)),
            member_count=self._extract_int(chat_data, ("member_count", "member_num")),
            owner_id=self._extract_value(chat_data, ("owner_id", "owner")),
            description=self._extract_value(chat_data, ("description",)),
            chat_mode=self._extract_value(chat_data, ("chat_mode",)),
            avatar_url=self._extract_value(chat_data, ("avatar_url", "avatar")),
            raw=dict(chat_data),
        )

    def _extract_member_items(self, data: dict[str, Any] | list[Any]) -> list[ChatMemberSummary]:
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("items") or data.get("members") or data.get("data") or []
        else:
            items = []

        summaries: list[ChatMemberSummary] = []
        for item in items or []:
            if not isinstance(item, dict):
                continue
            member_id = self._extract_value(item, ("member_id", "user_id", "open_id", "id"), default="")
            if not member_id:
                continue
            summaries.append(
                ChatMemberSummary(
                    member_id=member_id,
                    name=self._extract_value(item, ("name", "nickname")),
                    member_id_type=self._extract_value(item, ("member_id_type", "id_type")),
                    role=self._extract_value(item, ("role",)),
                    avatar_url=self._extract_value(item, ("avatar_url", "avatar")),
                    raw=dict(item),
                )
            )
        return summaries

    @staticmethod
    def _compact_dict(values: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in values.items() if value is not None}

    @staticmethod
    def _extract_value(data: Mapping[str, Any] | dict[str, Any], keys: tuple[str, ...], default: Any = None) -> Any:
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]
        return default

    @staticmethod
    def _extract_int(data: Mapping[str, Any] | dict[str, Any], keys: tuple[str, ...], default: int | None = None) -> int | None:
        value = ImChatAPIClient._extract_value(data, keys, default=default)
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _extract_string_list(data: Mapping[str, Any] | dict[str, Any], keys: tuple[str, ...]) -> list[str]:
        value = ImChatAPIClient._extract_value(data, keys, default=[])
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        return []


__all__ = [
    "ImChatAPIClient",
    "ImChatAPIError",
    "ImChatError",
    "ImChatTransportError",
    "ImChatValidationError",
    "build_http_client",
    "get_auth_headers",
]
