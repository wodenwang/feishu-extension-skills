from __future__ import annotations

import json

import httpx
import pytest

from feishu_extension_skills.services.im_chat.client import ImChatAPIClient, ImChatAPIError
from feishu_extension_skills.services.im_chat.models import AddChatMembersInput, CreateChatInput, DeleteChatInput, ListChatMembersInput, RemoveChatMemberInput


def test_client_create_merges_detail(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/im/v1/chats") and request.method == "POST":
            return httpx.Response(200, json={"code": 0, "msg": "ok", "data": {"chat_id": "oc_123"}})
        if request.url.path.endswith("/im/v1/chats/oc_123") and request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "code": 0,
                    "msg": "ok",
                    "data": {
                        "chat_id": "oc_123",
                        "name": "项目群",
                        "member_count": 3,
                        "owner_id": "ou_owner",
                    },
                },
            )
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    client = ImChatAPIClient(http_client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://open.feishu.cn"))
    monkeypatch.setattr(
        "feishu_extension_skills.services.im_chat.client.get_auth_headers",
        lambda auth_context: {"Authorization": "Bearer token"},
    )

    result = client.create_chat(
        {"app_id": "cli_xxx", "app_secret": "sec_xxx"},
        CreateChatInput.model_validate(
            {
                "app_id": "cli_xxx",
                "app_secret": "sec_xxx",
                "name": "项目群",
                "user_id_list": ["ou_1"],
            }
        ),
    )

    assert result.chat_id == "oc_123"
    assert result.name == "项目群"
    assert result.member_count == 3
    assert result.owner_id == "ou_owner"


def test_client_delete_chat_hits_delete_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[tuple[str, str, dict[str, str] | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.path, dict(request.url.params)))
        return httpx.Response(200, json={"code": 0, "msg": "success", "data": {}})

    client = ImChatAPIClient(http_client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://open.feishu.cn"))
    monkeypatch.setattr(
        "feishu_extension_skills.services.im_chat.client.get_auth_headers",
        lambda auth_context: {"Authorization": "Bearer token"},
    )

    result = client.delete_chat(
        DeleteChatInput.model_validate(
            {
                "app_id": "cli_xxx",
                "app_secret": "sec_xxx",
                "chat_id": "oc_123",
            }
        )
    )

    assert result.chat_id == "oc_123"
    assert result.status == "deleted"
    assert seen == [("DELETE", "/open-apis/im/v1/chats/oc_123", {})]


def test_client_list_members_parses_pagination(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.params["page_size"] == "20"
        assert request.url.params["page_token"] == "token-1"
        return httpx.Response(
            200,
            json={
                "code": 0,
                "msg": "ok",
                "data": {
                    "items": [
                        {"user_id": "ou_1", "name": "A"},
                        {"open_id": "ou_2", "name": "B"},
                    ],
                    "has_more": True,
                    "page_token": "token-2",
                },
            },
        )

    client = ImChatAPIClient(http_client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://open.feishu.cn"))
    monkeypatch.setattr(
        "feishu_extension_skills.services.im_chat.client.get_auth_headers",
        lambda auth_context: {"Authorization": "Bearer token"},
    )

    result = client.list_chat_members(
        ListChatMembersInput.model_validate(
            {
                "app_id": "cli_xxx",
                "app_secret": "sec_xxx",
                "chat_id": "oc_123",
                "page_size": 20,
                "page_token": "token-1",
            }
        )
    )

    assert result.chat_id == "oc_123"
    assert [item.member_id for item in result.items] == ["ou_1", "ou_2"]
    assert result.has_more is True
    assert result.page_token == "token-2"


def test_client_add_and_remove_members(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[tuple[str, str, dict[str, str] | None, dict[str, object] | None]] = []

    def request_json(request: httpx.Request) -> dict[str, object] | None:
        if not request.content:
            return None
        return json.loads(request.content.decode())

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            seen.append(("POST", request.url.path, dict(request.url.params), request_json(request)))
            return httpx.Response(200, json={"code": 0, "msg": "ok", "data": {"invalid_id_list": []}})
        if request.method == "DELETE":
            seen.append(("DELETE", request.url.path, dict(request.url.params), request_json(request)))
            return httpx.Response(200, json={"code": 0, "msg": "ok", "data": {"invalid_id_list": []}})
        raise AssertionError("unexpected request")

    client = ImChatAPIClient(http_client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://open.feishu.cn"))
    monkeypatch.setattr(
        "feishu_extension_skills.services.im_chat.client.get_auth_headers",
        lambda auth_context: {"Authorization": "Bearer token"},
    )

    add_result = client.add_chat_members(
        AddChatMembersInput.model_validate(
            {
                "app_id": "cli_xxx",
                "app_secret": "sec_xxx",
                "chat_id": "oc_123",
                "user_id_list": ["ou_1", "ou_1"],
                "member_id_type": "open_id",
            }
        )
    )
    remove_result = client.remove_chat_member(
        RemoveChatMemberInput.model_validate(
            {
                "app_id": "cli_xxx",
                "app_secret": "sec_xxx",
                "chat_id": "oc_123",
                "member_id": "ou_1",
                "member_id_type": "open_id",
            }
        )
    )

    assert add_result.added_member_ids == ["ou_1"]
    assert remove_result.removed_member_id == "ou_1"
    assert seen[0][0] == "POST"
    assert seen[0][1].endswith("/members")
    assert seen[0][2]["member_id_type"] == "open_id"
    assert seen[0][3] == {"id_list": ["ou_1"]}
    assert seen[1][0] == "DELETE"
    assert seen[1][1].endswith("/members")
    assert seen[1][2]["member_id_type"] == "open_id"
    assert seen[1][3] == {"id_list": ["ou_1"]}


def test_client_raises_api_error_on_nonzero_code(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"code": 190001, "msg": "no permission", "request_id": "req_1"})

    client = ImChatAPIClient(http_client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://open.feishu.cn"))
    monkeypatch.setattr(
        "feishu_extension_skills.services.im_chat.client.get_auth_headers",
        lambda auth_context: {"Authorization": "Bearer token"},
    )

    with pytest.raises(ImChatAPIError) as exc_info:
        client.get_chat({"app_id": "cli_xxx", "app_secret": "sec_xxx"}, "oc_123")

    assert "no permission" in str(exc_info.value)
    assert exc_info.value.details["code"] == 190001


def test_client_preserves_remote_error_semantics_on_invalid_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "code": 232006,
                "msg": "Your request specifies a chat_id which is invalid.",
                "error": {"log_id": "log-1"},
            },
        )

    client = ImChatAPIClient(http_client=httpx.Client(transport=httpx.MockTransport(handler), base_url="https://open.feishu.cn"))
    monkeypatch.setattr(
        "feishu_extension_skills.services.im_chat.client.get_auth_headers",
        lambda auth_context: {"Authorization": "Bearer token"},
    )

    with pytest.raises(ImChatAPIError) as exc_info:
        client.list_chat_members(
            ListChatMembersInput.model_validate(
                {
                    "app_id": "cli_xxx",
                    "app_secret": "sec_xxx",
                    "chat_id": "oc_invalid",
                }
            )
        )

    assert exc_info.value.details["status_code"] == 400
    assert exc_info.value.details["code"] == 232006
