from __future__ import annotations

import pytest
import httpx

from feishu_extension_skills.core.errors import FeishuAPIError
from feishu_extension_skills.core.http import build_http_client


def test_request_json_returns_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        return httpx.Response(
            200,
            json={
                "code": 0,
                "tenant_access_token": "token-123",
                "expire": 7200,
            },
        )

    client = build_http_client(
        base_url="https://open.feishu.cn",
        transport=httpx.MockTransport(handler),
    )

    payload = client.request_json("POST", "/open-apis/auth/v3/tenant_access_token/internal")

    assert payload["tenant_access_token"] == "token-123"
    assert payload["expire"] == 7200


def test_request_json_raises_feishu_api_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            json={
                "code": 1901,
                "msg": "permission denied",
                "request_id": "req-1",
            },
        )

    client = build_http_client(
        base_url="https://open.feishu.cn",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(FeishuAPIError) as exc_info:
        client.request_json("GET", "/open-apis/im/v1/chats/oc_123")

    error = exc_info.value
    assert error.code == "1901"
    assert error.status_code == 403
    assert error.request_id == "req-1"
    assert error.details["msg"] == "permission denied"
