from feishu_extension_skills.runtime.models import ActionResult, InvokeRequest


def test_invoke_request_model_validates_args() -> None:
    request = InvokeRequest.model_validate({"action": "feishu-chat-create", "args": {"name": "demo"}})

    assert request.action == "feishu-chat-create"
    assert request.args == {"name": "demo"}


def test_action_result_serializes_error_payload() -> None:
    result = ActionResult(
        ok=False,
        action="feishu-chat-create",
        data=None,
        error={"code": "validation_error", "message": "bad input", "details": {"field": "name"}},
    )

    payload = result.model_dump()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"
