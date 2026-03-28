from __future__ import annotations

import pytest

from feishu_extension_skills.core.config import AppConfig, load_config
from feishu_extension_skills.core.errors import ConfigError


def test_load_config_uses_environment_fallback() -> None:
    config = load_config(
        env={
            "FEISHU_APP_ID": "cli-app",
            "FEISHU_APP_SECRET": "cli-secret",
            "FEISHU_BASE_URL": "https://open.feishu.cn/",
            "FEISHU_TIMEOUT_SECONDS": "12",
            "FEISHU_TOKEN_REFRESH_SKEW_SECONDS": "30",
            "FEISHU_LOG_LEVEL": "debug",
        }
    )

    assert isinstance(config, AppConfig)
    assert config.app_id == "cli-app"
    assert config.app_secret == "cli-secret"
    assert config.base_url == "https://open.feishu.cn"
    assert config.timeout_seconds == 12.0
    assert config.token_refresh_skew_seconds == 30
    assert config.log_level == "debug"


def test_load_config_requires_app_credentials() -> None:
    with pytest.raises(ConfigError, match="app_id"):
        load_config(env={"FEISHU_APP_SECRET": "cli-secret"})

    with pytest.raises(ConfigError, match="app_secret"):
        load_config(env={"FEISHU_APP_ID": "cli-app"})
