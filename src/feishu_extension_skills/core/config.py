from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError as PydanticValidationError

from .errors import ConfigError


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    app_id: str
    app_secret: str
    base_url: str = "https://open.feishu.cn"
    timeout_seconds: float = Field(default=10.0, gt=0)
    token_refresh_skew_seconds: int = Field(default=60, ge=0)
    log_level: str = "INFO"

    def normalized_base_url(self) -> str:
        return self.base_url.rstrip("/")


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def load_config(
    *,
    app_id: str | None = None,
    app_secret: str | None = None,
    base_url: str | None = None,
    timeout_seconds: float | None = None,
    token_refresh_skew_seconds: int | None = None,
    log_level: str | None = None,
    env: Mapping[str, str] | None = None,
) -> AppConfig:
    environment = env or {}
    resolved_app_id = _coalesce(app_id, environment.get("FEISHU_APP_ID"))
    resolved_app_secret = _coalesce(app_secret, environment.get("FEISHU_APP_SECRET"))
    resolved_base_url = _coalesce(base_url, environment.get("FEISHU_BASE_URL"), "https://open.feishu.cn")
    resolved_timeout_seconds = _coalesce(timeout_seconds, environment.get("FEISHU_TIMEOUT_SECONDS"), 10.0)
    resolved_token_refresh_skew_seconds = _coalesce(
        token_refresh_skew_seconds,
        environment.get("FEISHU_TOKEN_REFRESH_SKEW_SECONDS"),
        60,
    )
    resolved_log_level = _coalesce(log_level, environment.get("FEISHU_LOG_LEVEL"), "INFO")

    if resolved_app_id is None:
        raise ConfigError("missing required configuration: app_id")
    if resolved_app_secret is None:
        raise ConfigError("missing required configuration: app_secret")

    try:
        timeout_value = float(resolved_timeout_seconds)
    except (TypeError, ValueError) as exc:
        raise ConfigError("invalid configuration: timeout_seconds") from exc

    try:
        skew_value = int(resolved_token_refresh_skew_seconds)
    except (TypeError, ValueError) as exc:
        raise ConfigError("invalid configuration: token_refresh_skew_seconds") from exc

    normalized_base_url = str(resolved_base_url).rstrip("/")
    if not normalized_base_url:
        raise ConfigError("invalid configuration: base_url")

    try:
        return AppConfig(
            app_id=str(resolved_app_id),
            app_secret=str(resolved_app_secret),
            base_url=normalized_base_url,
            timeout_seconds=timeout_value,
            token_refresh_skew_seconds=skew_value,
            log_level=str(resolved_log_level),
        )
    except PydanticValidationError as exc:
        raise ConfigError(f"invalid configuration: {exc}") from exc
