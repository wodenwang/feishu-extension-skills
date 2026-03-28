from __future__ import annotations

import httpx

from feishu_extension_skills.auth.models import AuthContext
from feishu_extension_skills.auth.provider import fetch_tenant_access_token
from feishu_extension_skills.core.http import build_http_client


def test_fetch_tenant_access_token_parses_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/open-apis/auth/v3/tenant_access_token/internal"
        return httpx.Response(
            200,
            json={
                "code": 0,
                "tenant_access_token": "tenant-token",
                "expire": 3600,
            },
        )

    client = build_http_client(
        base_url="https://open.feishu.cn",
        transport=httpx.MockTransport(handler),
    )
    auth_context = AuthContext(
        app_id="cli-app",
        app_secret="cli-secret",
        base_url="https://open.feishu.cn",
        timeout_seconds=10.0,
        token_refresh_skew_seconds=60,
    )

    response = fetch_tenant_access_token(auth_context, client=client)

    assert response.tenant_access_token == "tenant-token"
    assert response.expire == 3600
