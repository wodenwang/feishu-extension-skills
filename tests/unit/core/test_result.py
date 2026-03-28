from __future__ import annotations

from feishu_extension_skills.core.result import error_result, ok_result


def test_ok_result_shape() -> None:
    result = ok_result("feishu.chat.create", {"chat_id": "oc_123"})

    assert result.model_dump() == {
        "ok": True,
        "action": "feishu.chat.create",
        "data": {"chat_id": "oc_123"},
        "error": None,
    }


def test_error_result_shape() -> None:
    result = error_result(
        "feishu.chat.member.remove",
        "validation_error",
        "member_id is required",
        details={"field": "member_id"},
    )

    assert result.model_dump() == {
        "ok": False,
        "action": "feishu.chat.member.remove",
        "data": None,
        "error": {
            "code": "validation_error",
            "message": "member_id is required",
            "details": {"field": "member_id"},
        },
    }
