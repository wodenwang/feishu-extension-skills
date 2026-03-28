from __future__ import annotations

from feishu_extension_skills.services.im_chat.actions import ACTION_HANDLERS, FEISHU_CHAT_CREATE, FEISHU_CHAT_DELETE, FEISHU_CHAT_MEMBER_ADD, FEISHU_CHAT_MEMBER_REMOVE, FEISHU_CHAT_MEMBERS_LIST, invoke_action
from feishu_extension_skills.services.im_chat.models import ChatMembersPage, ChatOperationResult, ChatSummary
from feishu_extension_skills.services.im_chat.service import ImChatService, add_chat_members_action, create_chat_action, delete_chat_action, list_chat_members_action, remove_chat_member_action


class FakeClient:
    def create_chat(self, auth_context, payload):
        return ChatSummary(chat_id="oc_123", name=payload.name, member_count=2, owner_id="ou_owner")

    def list_chat_members(self, payload):
        return ChatMembersPage(chat_id=payload.chat_id, items=[], has_more=False, page_token=None)

    def add_chat_members(self, payload):
        return ChatOperationResult(chat_id=payload.chat_id, added_member_ids=payload.user_id_list, failed_member_ids=[])

    def delete_chat(self, payload):
        return ChatOperationResult(chat_id=payload.chat_id, status="deleted")

    def remove_chat_member(self, payload):
        return ChatOperationResult(chat_id=payload.chat_id, removed_member_id=payload.member_id)

    def get_chat(self, auth_context, chat_id, fallback=None):
        return fallback or ChatSummary(chat_id=chat_id)


def test_action_registry_covers_first_phase_actions() -> None:
    assert set(ACTION_HANDLERS) == {
        FEISHU_CHAT_CREATE,
        FEISHU_CHAT_DELETE,
        FEISHU_CHAT_MEMBERS_LIST,
        FEISHU_CHAT_MEMBER_ADD,
        FEISHU_CHAT_MEMBER_REMOVE,
    }


def test_action_handlers_return_expected_payloads() -> None:
    service = ImChatService(client=FakeClient())

    create_payload = {
        "app_id": "cli_xxx",
        "app_secret": "sec_xxx",
        "name": "项目群",
        "user_id_list": ["ou_1"],
    }
    list_payload = {
        "app_id": "cli_xxx",
        "app_secret": "sec_xxx",
        "chat_id": "oc_123",
    }
    add_payload = {
        "app_id": "cli_xxx",
        "app_secret": "sec_xxx",
        "chat_id": "oc_123",
        "user_id_list": ["ou_1"],
    }
    delete_payload = {
        "app_id": "cli_xxx",
        "app_secret": "sec_xxx",
        "chat_id": "oc_123",
    }
    remove_payload = {
        "app_id": "cli_xxx",
        "app_secret": "sec_xxx",
        "chat_id": "oc_123",
        "member_id": "ou_1",
    }

    assert create_chat_action(create_payload, service)["chat_id"] == "oc_123"
    assert delete_chat_action(delete_payload, service)["status"] == "deleted"
    assert list_chat_members_action(list_payload, service)["chat_id"] == "oc_123"
    assert add_chat_members_action(add_payload, service)["added_member_ids"] == ["ou_1"]
    assert remove_chat_member_action(remove_payload, service)["removed_member_id"] == "ou_1"


def test_invoke_action_dispatches() -> None:
    service = ImChatService(client=FakeClient())
    result = invoke_action(
        FEISHU_CHAT_CREATE,
        {
            "app_id": "cli_xxx",
            "app_secret": "sec_xxx",
            "name": "项目群",
            "user_id_list": ["ou_1"],
        },
        service=service,
    )

    assert result["chat_id"] == "oc_123"
