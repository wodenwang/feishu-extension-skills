from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict, Tuple

from feishu_extension_skills.auth.models import AuthContext, TokenCacheEntry
from feishu_extension_skills.auth.provider import fetch_tenant_access_token
from feishu_extension_skills.core.errors import ConfigError


class TokenManager:
    def __init__(self) -> None:
        self._cache: Dict[Tuple[str, str, str], TokenCacheEntry] = {}
        self._lock = Lock()

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def get_tenant_access_token(self, auth_context: AuthContext) -> str:
        cache_key = self._cache_key(auth_context)
        now = datetime.now(timezone.utc)
        with self._lock:
            cached = self._cache.get(cache_key)
            if cached and cached.is_valid(
                skew_seconds=auth_context.token_refresh_skew_seconds,
                now=now,
            ):
                return cached.tenant_access_token

        response = fetch_tenant_access_token(auth_context)
        expire_at = response.fetched_at + timedelta(seconds=response.expire)
        entry = TokenCacheEntry(
            tenant_access_token=response.tenant_access_token,
            expire_at=expire_at,
            fetched_at=response.fetched_at,
        )
        with self._lock:
            self._cache[cache_key] = entry
        return entry.tenant_access_token

    def get_auth_headers(self, auth_context: AuthContext) -> dict[str, str]:
        token = self.get_tenant_access_token(auth_context)
        return {"Authorization": f"Bearer {token}"}

    def _cache_key(self, auth_context: AuthContext) -> tuple[str, str, str]:
        if not auth_context.app_id:
            raise ConfigError("missing required configuration: app_id")
        if not auth_context.app_secret:
            raise ConfigError("missing required configuration: app_secret")
        return (auth_context.base_url.rstrip("/"), auth_context.app_id, auth_context.app_secret)


_TOKEN_MANAGER = TokenManager()


def get_tenant_access_token(auth_context: AuthContext) -> str:
    return _TOKEN_MANAGER.get_tenant_access_token(auth_context)


def get_auth_headers(auth_context: AuthContext) -> dict[str, str]:
    return _TOKEN_MANAGER.get_auth_headers(auth_context)
