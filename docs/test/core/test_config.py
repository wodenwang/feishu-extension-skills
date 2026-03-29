from __future__ import annotations

import json

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


def test_load_config_uses_local_file_before_environment(tmp_path, monkeypatch) -> None:
    local_dir = tmp_path / ".local"
    local_dir.mkdir()
    (local_dir / "feishu-extension-skills.json").write_text(
        json.dumps(
            {
                "app_id": "file-app",
                "app_secret": "file-secret",
                "base_url": "https://file.example.com/",
                "timeout_seconds": 22,
                "token_refresh_skew_seconds": 45,
                "log_level": "warning",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    config = load_config(
        env={
            "FEISHU_APP_ID": "env-app",
            "FEISHU_APP_SECRET": "env-secret",
            "FEISHU_BASE_URL": "https://env.example.com/",
            "FEISHU_TIMEOUT_SECONDS": "12",
            "FEISHU_TOKEN_REFRESH_SKEW_SECONDS": "30",
            "FEISHU_LOG_LEVEL": "debug",
        }
    )

    assert config.app_id == "file-app"
    assert config.app_secret == "file-secret"
    assert config.base_url == "https://file.example.com"
    assert config.timeout_seconds == 22.0
    assert config.token_refresh_skew_seconds == 45
    assert config.log_level == "warning"


def test_load_config_prefers_explicit_args_over_local_file_and_environment() -> None:
    config = load_config(
        app_id="arg-app",
        app_secret="arg-secret",
        base_url="https://arg.example.com/",
        timeout_seconds=33,
        token_refresh_skew_seconds=55,
        log_level="error",
        env={
            "FEISHU_APP_ID": "env-app",
            "FEISHU_APP_SECRET": "env-secret",
        },
        local_config={
            "app_id": "file-app",
            "app_secret": "file-secret",
            "base_url": "https://file.example.com/",
            "timeout_seconds": 22,
            "token_refresh_skew_seconds": 45,
            "log_level": "warning",
        },
    )

    assert config.app_id == "arg-app"
    assert config.app_secret == "arg-secret"
    assert config.base_url == "https://arg.example.com"
    assert config.timeout_seconds == 33.0
    assert config.token_refresh_skew_seconds == 55
    assert config.log_level == "error"


def test_load_config_supports_explicit_config_file_path(tmp_path) -> None:
    config_file = tmp_path / "feishu-config.json"
    config_file.write_text(
        json.dumps(
            {
                "app_id": "custom-file-app",
                "app_secret": "custom-file-secret",
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_file=config_file, env={})

    assert config.app_id == "custom-file-app"
    assert config.app_secret == "custom-file-secret"


def test_load_config_requires_app_credentials() -> None:
    with pytest.raises(ConfigError, match="app_id"):
        load_config(env={"FEISHU_APP_SECRET": "cli-secret"})

    with pytest.raises(ConfigError, match="app_secret"):
        load_config(env={"FEISHU_APP_ID": "cli-app"})
