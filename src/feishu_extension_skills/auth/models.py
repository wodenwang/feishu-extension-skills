from __future__ import annotations

from datetime import datetime, timezone
from datetime import timedelta

from pydantic import BaseModel, ConfigDict, Field

from feishu_extension_skills.core.config import AppConfig


class AuthContext(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    app_id: str
    app_secret: str
    base_url: str = "https://open.feishu.cn"
    timeout_seconds: float = Field(default=10.0, gt=0)
    token_refresh_skew_seconds: int = Field(default=60, ge=0)

    @classmethod
    def from_config(cls, config: AppConfig) -> "AuthContext":
        return cls(
            app_id=config.app_id,
            app_secret=config.app_secret,
            base_url=config.base_url,
            timeout_seconds=config.timeout_seconds,
            token_refresh_skew_seconds=config.token_refresh_skew_seconds,
        )


class TenantAccessTokenResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    tenant_access_token: str
    expire: int = Field(default=7200, ge=1)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TokenCacheEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_access_token: str
    expire_at: datetime
    fetched_at: datetime

    def is_valid(self, *, skew_seconds: int, now: datetime | None = None) -> bool:
        current_time = now or datetime.now(timezone.utc)
        return self.expire_at > current_time + timedelta(seconds=skew_seconds)
