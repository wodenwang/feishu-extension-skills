from __future__ import annotations

from datetime import datetime, timedelta, timezone

from feishu_extension_skills.auth.models import AuthContext, TenantAccessTokenResponse, TokenCacheEntry
from feishu_extension_skills.auth import token_manager


def _auth_context() -> AuthContext:
    return AuthContext(
        app_id="cli-app",
        app_secret="cli-secret",
        base_url="https://open.feishu.cn",
        timeout_seconds=10.0,
        token_refresh_skew_seconds=60,
    )


def test_get_tenant_access_token_uses_cache(monkeypatch) -> None:
    token_manager._TOKEN_MANAGER.clear()
    calls: list[str] = []

    def fake_fetch(auth_context: AuthContext) -> TenantAccessTokenResponse:
        calls.append(auth_context.app_id)
        return TenantAccessTokenResponse(
            tenant_access_token=f"token-{len(calls)}",
            expire=3600,
            fetched_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(token_manager, "fetch_tenant_access_token", fake_fetch)

    first = token_manager.get_tenant_access_token(_auth_context())
    second = token_manager.get_tenant_access_token(_auth_context())

    assert first == "token-1"
    assert second == "token-1"
    assert calls == ["cli-app"]


def test_get_tenant_access_token_refreshes_expiring_cache(monkeypatch) -> None:
    token_manager._TOKEN_MANAGER.clear()
    now = datetime.now(timezone.utc)
    cache_key = ("https://open.feishu.cn", "cli-app", "cli-secret")
    token_manager._TOKEN_MANAGER._cache[cache_key] = TokenCacheEntry(
        tenant_access_token="stale-token",
        expire_at=now + timedelta(seconds=10),
        fetched_at=now,
    )
    calls: list[str] = []

    def fake_fetch(auth_context: AuthContext) -> TenantAccessTokenResponse:
        calls.append(auth_context.app_id)
        return TenantAccessTokenResponse(
            tenant_access_token="fresh-token",
            expire=3600,
            fetched_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(token_manager, "fetch_tenant_access_token", fake_fetch)

    token = token_manager.get_tenant_access_token(_auth_context())

    assert token == "fresh-token"
    assert calls == ["cli-app"]


def test_get_auth_headers_returns_bearer_header(monkeypatch) -> None:
    token_manager._TOKEN_MANAGER.clear()

    def fake_fetch(_: AuthContext) -> TenantAccessTokenResponse:
        return TenantAccessTokenResponse(
            tenant_access_token="header-token",
            expire=3600,
            fetched_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(token_manager, "fetch_tenant_access_token", fake_fetch)

    headers = token_manager.get_auth_headers(_auth_context())

    assert headers == {"Authorization": "Bearer header-token"}
