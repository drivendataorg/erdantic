from importlib import import_module
from pathlib import Path
from typing import List

import typer

from erdantic.erd import create
from erdantic.version import __version__


app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.command()
def main(
    models: List[str] = typer.Argument(
        ...,
        help=(
            "One or more full module paths to root data model classes to include in diagram, "
            "e.g., 'erdantic.examples.pydantic.Party'."
        ),
    ),
    out: Path = typer.Option("./diagram.png", "--out", "-o", help="Output filename."),
    overwrite: bool = typer.Option(False, help="Whether to overwrite an existing file."),
    dot: bool = typer.Option(
        False,
        "--dot",
        "-d",
        help="Print out Graphviz DOT code for generated graph to console. Ignores --out option.",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show erdantic version.",
    ),
):
    """Draw entity relationship diagrams (ERDs) for Python data model classes. Diagrams are
    rendered using the venerable Graphviz library. Supported data modeling frameworks are Pydantic
    and dataclasses from the standard library.
    """
    model_classes = []
    for model in models:
        module_name, model_name = model.rsplit(".", 1)
        module = import_module(module_name)
        model_classes.append(getattr(module, model_name))

    diagram = create(*model_classes)
    if dot:
        typer.echo(diagram.to_dot())
    else:
        if out.exists() and not overwrite:
            typer.echo(f"{out} already exists. To overwrite, use the --overwrite flag.")
            raise typer.Exit(code=1)
        diagram.draw(out)
        typer.echo(f"Rendered diagram to {out}")
