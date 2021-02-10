from importlib import import_module
from pathlib import Path
from typing import List, Optional

import typer

from erdantic.erd import create
from erdantic.version import __version__


app = typer.Typer()


def version_callback(version: bool):
    """Print erdantic version to console."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


def dot_callback(ctx: typer.Context, dot: bool):
    """Set --out to not be required since we're going to ignore it."""
    if dot:
        for param in ctx.command.params:
            if param.name == "out":
                param.required = False
    return dot


@app.command()
def main(
    models: List[str] = typer.Argument(
        ...,
        help=(
            "One or more full dotted paths to data model classes to include in diagram, "
            "e.g., 'erdantic.examples.pydantic.Party'. Only the root models of composition trees "
            "are needed; erdantic will traverse the composition tree to find component classes."
        ),
    ),
    out: Path = typer.Option(..., "--out", "-o", help="Output filename."),
    dot: Optional[bool] = typer.Option(
        None,
        "--dot",
        "-d",
        callback=dot_callback,
        help=(
            "Print out Graphviz DOT language representation for generated graph to console "
            "instead of rendering an image. The --out option will be ignored."
        ),
    ),
    no_overwrite: Optional[bool] = typer.Option(
        None, "--no-overwrite", help="Prevent overwriting an existing file."
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show erdantic version and exit.",
    ),
):
    """Draw entity relationship diagrams (ERDs) for Python data model classes. Diagrams are
    rendered using the Graphviz library. Currently supported data modeling frameworks are Pydantic
    and standard library dataclasses.
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
        if out.exists() and no_overwrite:
            typer.echo(f"{out} already exists, and you specified --no-overwrite.")
            raise typer.Exit(code=1)
        diagram.draw(out)
        typer.echo(f"Rendered diagram to {out}")
