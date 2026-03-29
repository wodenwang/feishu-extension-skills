from typer.testing import CliRunner

from feishu_extension_skills.cli.app import app
from feishu_extension_skills.runtime.dispatcher import ActionDispatcher, ActionRegistry


def test_cli_invoke_outputs_action_result_json(monkeypatch) -> None:
    registry = ActionRegistry()
    dispatcher = ActionDispatcher(registry, loader=lambda _: None)
    dispatcher.register("demo.echo", lambda request: {"echo": request.args["value"]})

    monkeypatch.setattr("feishu_extension_skills.cli.app.get_dispatcher", lambda: dispatcher)

    runner = CliRunner()
    result = runner.invoke(app, ["invoke", "demo.echo", "--args-json", '{"value":"hello"}'])

    assert result.exit_code == 0
    assert '"ok": true' in result.stdout
    assert '"echo": "hello"' in result.stdout


def test_cli_invoke_bad_json_returns_validation_error(monkeypatch) -> None:
    dispatcher = ActionDispatcher(ActionRegistry(), loader=lambda _: None)
    monkeypatch.setattr("feishu_extension_skills.cli.app.get_dispatcher", lambda: dispatcher)

    runner = CliRunner()
    result = runner.invoke(app, ["invoke", "demo.echo", "--args-json", "{bad json}"])

    assert result.exit_code == 1
    assert '"ok": false' in result.stdout
    assert '"validation_error"' in result.stdout


def test_cli_invoke_unknown_action_returns_action_not_found(monkeypatch) -> None:
    dispatcher = ActionDispatcher(ActionRegistry(), loader=lambda _: None)
    monkeypatch.setattr("feishu_extension_skills.cli.app.get_dispatcher", lambda: dispatcher)

    runner = CliRunner()
    result = runner.invoke(app, ["invoke", "demo.missing", "--args-json", "{}"])

    assert result.exit_code == 1
    assert '"ok": false' in result.stdout
    assert '"action_not_found"' in result.stdout


def test_cli_invoke_passes_config_file(monkeypatch, tmp_path) -> None:
    registry = ActionRegistry()
    dispatcher = ActionDispatcher(registry, loader=lambda _: None)
    config_file = tmp_path / "feishu-config.json"
    config_file.write_text('{"app_id":"cli_xxx","app_secret":"sec_xxx"}', encoding="utf-8")

    def handler(request):
        return {"config_file": request.args["config_file"]}

    dispatcher.register("demo.echo", handler)
    monkeypatch.setattr("feishu_extension_skills.cli.app.get_dispatcher", lambda: dispatcher)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["invoke", "demo.echo", "--args-json", '{"value":"hello"}', "--config-file", str(config_file)],
    )

    assert result.exit_code == 0
    assert f'"config_file": "{config_file}"' in result.stdout
