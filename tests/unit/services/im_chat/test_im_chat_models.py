from __future__ import annotations

import pytest

from feishu_extension_skills.services.im_chat.models import (
    AddChatMembersInput,
    CreateChatInput,
    DeleteChatInput,
    ListChatMembersInput,
    RemoveChatMemberInput,
)


def test_create_chat_input_dedupes_members() -> None:
    payload = CreateChatInput.model_validate(
        {
            "app_id": "cli_xxx",
            "app_secret": "sec_xxx",
            "name": "项目群",
            "user_id_list": ["ou_1", "ou_2", "ou_1", " ou_2 "],
        }
    )

    assert payload.user_id_list == ["ou_1", "ou_2"]


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"app_id": "cli_xxx", "app_secret": "sec_xxx", "name": "群", "user_id_list": []}, "user_id_list"),
        ({"app_id": "cli_xxx", "app_secret": "sec_xxx", "chat_id": ""}, "chat_id"),
        ({"app_id": "cli_xxx", "app_secret": "sec_xxx", "chat_id": "oc_xxx", "page_size": 0}, "page_size"),
        ({"app_id": "cli_xxx", "app_secret": "sec_xxx", "chat_id": "oc_xxx", "user_id_list": []}, "user_id_list"),
        ({"app_id": "cli_xxx", "app_secret": "sec_xxx", "chat_id": "oc_xxx", "member_id": ""}, "member_id"),
    ],
)
def test_models_validate_required_inputs(payload: dict[str, object], field: str) -> None:
    with pytest.raises(ValueError):
        if "name" in payload:
            CreateChatInput.model_validate(payload)
        elif payload.get("chat_id") == "":
            DeleteChatInput.model_validate(
                {
                    "app_id": payload["app_id"],
                    "app_secret": payload["app_secret"],
                    "chat_id": "",
                }
            )
        elif "page_size" in payload:
            ListChatMembersInput.model_validate(payload)
        elif "user_id_list" in payload:
            AddChatMembersInput.model_validate(payload)
        else:
            RemoveChatMemberInput.model_validate(payload)


def test_member_id_type_must_be_known() -> None:
    with pytest.raises(ValueError):
        ListChatMembersInput.model_validate(
            {
                "app_id": "cli_xxx",
                "app_secret": "sec_xxx",
                "chat_id": "oc_xxx",
                "member_id_type": "invalid",
            }
        )
