"""Command line interface for invoking phase-1 actions."""

from __future__ import annotations

import typer

from feishu_extension_skills.core.result import error_result
from feishu_extension_skills.runtime.dispatcher import get_dispatcher
from feishu_extension_skills.runtime.errors import ValidationError
from feishu_extension_skills.runtime.validators import parse_args_json

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Invoke Feishu extension actions.")


@app.callback()
def cli_root() -> None:
    """Root command group for feishu_extension_skills."""


@app.command()
def invoke(
    action: str = typer.Argument(..., help="Action name to invoke"),
    args_json: str = typer.Option("{}", "--args-json", help="JSON string with action arguments"),
    config_file: str | None = typer.Option(None, "--config-file", help="Path to local JSON config file"),
) -> None:
    dispatcher = get_dispatcher()
    try:
        args = parse_args_json(args_json)
    except ValidationError as exc:
        result = error_result(action, exc.code, str(exc), details=exc.details)
        typer.echo(result.model_dump_json(indent=2))
        raise typer.Exit(code=1)
    if config_file is not None:
        args["config_file"] = config_file
    result = dispatcher.invoke(action, args)
    typer.echo(result.model_dump_json(indent=2))
    raise typer.Exit(code=0 if result.ok else 1)


def main() -> None:
    app()
