"""Command line interface for invoking phase-1 actions."""

from __future__ import annotations

import typer

from feishu_extension_skills.runtime.dispatcher import get_dispatcher

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Invoke Feishu extension actions.")


@app.callback()
def cli_root() -> None:
    """Root command group for feishu_extension_skills."""


@app.command()
def invoke(
    action: str = typer.Argument(..., help="Action name to invoke"),
    args_json: str = typer.Option("{}", "--args-json", help="JSON string with action arguments"),
) -> None:
    dispatcher = get_dispatcher()
    result = dispatcher.invoke(action, args_json)
    typer.echo(result.model_dump_json(indent=2))
    raise typer.Exit(code=0 if result.ok else 1)


def main() -> None:
    app()
