from feishu_extension_skills.runtime.actions import FEISHU_CHAT_DISBAND
from feishu_extension_skills.runtime.dispatcher import ActionDispatcher, ActionRegistry
from feishu_extension_skills.runtime.errors import ActionNotFoundError, ValidationError
from feishu_extension_skills.runtime.models import InvokeRequest
import feishu_extension_skills.services.im_chat.actions as im_chat_actions


def test_dispatcher_registers_and_invokes_handler() -> None:
    registry = ActionRegistry()
    dispatcher = ActionDispatcher(registry, loader=lambda _: None)

    def handler(request: InvokeRequest) -> dict[str, object]:
        return {"echo": request.args["value"]}

    dispatcher.register("demo.echo", handler)

    result = dispatcher.dispatch(InvokeRequest(action="demo.echo", args={"value": "hello"}))

    assert result.ok is True
    assert result.action == "demo.echo"
    assert result.data == {"echo": "hello"}


def test_dispatcher_reports_unknown_action() -> None:
    dispatcher = ActionDispatcher(ActionRegistry(), loader=lambda _: None)

    result = dispatcher.dispatch(InvokeRequest(action="demo.missing", args={}))

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "action_not_found"


def test_register_rejects_duplicate_action_name() -> None:
    registry = ActionRegistry()
    registry.register("demo.echo", lambda request: request.args)

    try:
        registry.register("demo.echo", lambda request: request.args)
    except ValidationError as exc:
        assert exc.code == "validation_error"
    else:  # pragma: no cover
        raise AssertionError("expected duplicate registration to fail")


def test_dispatcher_lazy_loads_disband_action(monkeypatch) -> None:
    def fake_disband_chat_action(args, service=None):
        return {"chat_id": args["chat_id"], "status": "disbanded"}

    monkeypatch.setattr(im_chat_actions, "disband_chat_action", fake_disband_chat_action)

    dispatcher = ActionDispatcher(ActionRegistry())
    result = dispatcher.dispatch(
        InvokeRequest(
            action=FEISHU_CHAT_DISBAND,
            args={
                "app_id": "cli_xxx",
                "app_secret": "sec_xxx",
                "chat_id": "oc_123",
            },
        )
    )

    assert result.ok is True
    assert result.data == {"chat_id": "oc_123", "status": "disbanded"}
