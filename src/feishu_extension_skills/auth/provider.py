from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from feishu_extension_skills.auth.models import AuthContext, TenantAccessTokenResponse
from feishu_extension_skills.core.errors import FeishuAPIError
from feishu_extension_skills.core.http import HttpClient, build_http_client

TOKEN_ENDPOINT = "/open-apis/auth/v3/tenant_access_token/internal"


def fetch_tenant_access_token(
    auth_context: AuthContext,
    *,
    client: HttpClient | None = None,
) -> TenantAccessTokenResponse:
    http_client = client or build_http_client(
        base_url=auth_context.base_url,
        timeout_seconds=auth_context.timeout_seconds,
    )
    payload = http_client.request_json(
        "POST",
        TOKEN_ENDPOINT,
        json={
            "app_id": auth_context.app_id,
            "app_secret": auth_context.app_secret,
        },
    )
    token = _extract_token(payload)
    expire = _extract_expire(payload)
    return TenantAccessTokenResponse(
        tenant_access_token=token,
        expire=expire,
        fetched_at=datetime.now(timezone.utc),
    )


def _extract_token(payload: dict[str, Any]) -> str:
    token = payload.get("tenant_access_token")
    if token:
        return str(token)
    data = payload.get("data")
    if isinstance(data, dict) and data.get("tenant_access_token"):
        return str(data["tenant_access_token"])
    raise FeishuAPIError(
        code="invalid_response",
        message="tenant_access_token is missing from feishu response",
        details=payload,
    )


def _extract_expire(payload: dict[str, Any]) -> int:
    expire = payload.get("expire")
    if expire is None:
        data = payload.get("data")
        if isinstance(data, dict):
            expire = data.get("expire")
    if expire is None:
        return 7200
    try:
        return int(expire)
    except (TypeError, ValueError) as exc:
        raise FeishuAPIError(
            code="invalid_response",
            message="expire is invalid in feishu response",
            details=payload,
        ) from exc
