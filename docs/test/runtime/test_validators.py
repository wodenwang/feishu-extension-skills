import pytest

from feishu_extension_skills.runtime.errors import ValidationError
from feishu_extension_skills.runtime.validators import normalize_invoke_request, parse_args_json


def test_parse_args_json_returns_mapping() -> None:
    assert parse_args_json('{"name":"demo"}') == {"name": "demo"}


def test_parse_args_json_rejects_non_object() -> None:
    with pytest.raises(ValidationError) as exc_info:
        parse_args_json("[]")

    assert exc_info.value.code == "validation_error"


def test_normalize_invoke_request_strips_action() -> None:
    request = normalize_invoke_request("  demo.echo  ", '{"value": 1}')

    assert request.action == "demo.echo"
    assert request.args == {"value": 1}

